require "json"
require_relative "base"

module Boukensha
  module Backends
    class AzureFoundry < Base
      MODELS = {
        "gpt-5.5" => {
          context_window: 1_000_000,
          cost_per_million: { input: 5.0, output: 30.0 },
          usage_unit: :tokens
        },
        "gpt-5.4" => {
          context_window: 1_000_000,
          cost_per_million: { input: 2.5, output: 15.0 },
          usage_unit: :tokens
        },
        "gpt-5.4-mini" => {
          context_window: 400_000,
          cost_per_million: { input: 0.75, output: 4.5 },
          usage_unit: :tokens
        }
      }.freeze

      def initialize(api_key:, endpoint:, model:)
        @api_key  = api_key
        @endpoint = endpoint.chomp("/")
        configure_model(model)
      end

      def to_messages(system, messages)
        input = []

        messages.each do |msg|
          case msg.role
          when :tool_result
            input << {
              type: "function_call_output",
              call_id: msg.tool_use_id,
              output: msg.content
            }
          when :assistant
            if msg.content.is_a?(String)
              input << { role: "assistant", content: msg.content } unless msg.content.empty?
            elsif msg.content.is_a?(Array)
              text_blocks = msg.content.select { |b| b["type"] == "text" }
              tool_blocks = msg.content.select { |b| b["type"] == "tool_use" }

              text = text_blocks.map { |b| b["text"] }.join
              input << { role: "assistant", content: text } unless text.empty?

              tool_blocks.each do |b|
                args = b["input"].is_a?(String) ? b["input"] : b["input"].to_json
                input << {
                  type: "function_call",
                  call_id: b["id"],
                  name: b["name"],
                  arguments: args
                }
              end
            end
          else
            input << { role: msg.role.to_s, content: msg.content }
          end
        end

        input
      end

      def to_tools(tools)
        tools.values.map do |tool|
          {
            type: "function",
            name: tool.name,
            description: tool.description,
            parameters: {
              type: "object",
              properties: tool.parameters,
              required: tool.parameters.keys.map(&:to_s)
            }
          }
        end
      end

      def to_payload(context, max_output_tokens: 1024)
        payload = {
          model: @model,
          instructions: context.system,
          input: to_messages(context.system, context.messages),
          tools: to_tools(context.tools),
          max_output_tokens: max_output_tokens
        }

        payload.delete(:instructions) if context.system.nil? || context.system.empty?
        payload
      end

      def headers
        {
          "Content-Type" => "application/json",
          "api-key"      => @api_key
        }
      end

      def url
        "#{@endpoint}/openai/v1/responses"
      end
    end
  end
end
