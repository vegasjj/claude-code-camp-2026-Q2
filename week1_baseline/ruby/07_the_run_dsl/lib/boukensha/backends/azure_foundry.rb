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

      def to_payload(context, max_output_tokens: 1024, tools: nil)
        effective_tools = tools.nil? ? to_tools(context.tools) : tools

        payload = {
          model: @model,
          instructions: context.system,
          input: to_messages(context.system, context.messages),
          tools: effective_tools,
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

      def parse_response(response)
        content = []
        tool_calls = []

        if response["output"].is_a?(Array)
          response["output"].each do |item|
            case item["type"]
            when "output_text", "text"
              content << { "type" => "text", "text" => item["text"] } if item["text"]
            when "tool_call", "function_call", "function"
              tc = extract_tool_call(item)
              if tc
                tool_calls << tc
                content << tc
              end
            when "message", nil
              if item["content"].is_a?(String)
                content << { "type" => "text", "text" => item["content"] } unless item["content"].empty?
              elsif item["content"].is_a?(Array)
                item["content"].each do |block|
                  case block["type"]
                  when "output_text", "text"
                    content << { "type" => "text", "text" => block["text"] } if block["text"]
                  when "tool_call", "function_call", "function"
                    tc = extract_tool_call(block)
                    if tc
                      tool_calls << tc
                      content << tc
                    end
                  end
                end
              elsif item["text"].is_a?(String)
                content << { "type" => "text", "text" => item["text"] } unless item["text"].empty?
              end
            end
          end
        elsif response["choices"].is_a?(Array)
          message = response.dig("choices", 0, "message") || {}
          t_calls = message["tool_calls"] || []

          content << { "type" => "text", "text" => message["content"] } if message["content"] && !message["content"].empty?

          t_calls.each do |tc|
            parsed_tc = extract_tool_call(tc)
            if parsed_tc
              tool_calls << parsed_tc
              content << parsed_tc
            end
          end
        end

        if content.empty? && response["output_text"].is_a?(String)
          content << { "type" => "text", "text" => response["output_text"] }
        end

        { stop_reason: tool_calls.empty? ? "end_turn" : "tool_use", content: content }
      end

      private

      def extract_tool_call(block)
        fn = block["function"].is_a?(Hash) ? block["function"] : block
        name = fn["name"] || block["name"]
        return nil unless name

        raw_args = fn["arguments"] || block["arguments"] || fn["input"] || block["input"] || {}
        args = raw_args.is_a?(String) ? (JSON.parse(raw_args) rescue {}) : raw_args
        call_id = block["call_id"] || block["id"] || fn["id"] || name

        {
          "type"  => "tool_use",
          "id"    => call_id,
          "name"  => name,
          "input" => args
        }
      end
    end
  end
end
