# Azure Foundry Backend Implementation Plan

## Goal

Add a new `AzureFoundry` backend to the Boukensha backends directory that enables interaction with Azure AI Foundry deployments of OpenAI models using the **Responses API** (`/v1/responses`), following the established backend contract defined in [base.rb](file:///workspaces/claude-code-camp-2026-Q2/week1_baseline/ruby/03_prompt_builder/lib/boukensha/backends/base.rb).

### Background

The existing [OpenAI backend](file:///workspaces/claude-code-camp-2026-Q2/week1_baseline/ruby/03_prompt_builder/lib/boukensha/backends/openai.rb) uses the **Chat Completions API** (`/v1/chat/completions`) with a `messages` array. The requirement explicitly states the new Azure Foundry backend must use the **Responses API** instead. The Responses API has a different payload structure:

| Aspect | Chat Completions API | Responses API |
|:---|:---|:---|
| **Endpoint** | `/v1/chat/completions` | `/v1/responses` |
| **Messages field** | `messages` array | `input` array |
| **System prompt** | `role: "system"` message in array | Top-level `instructions` field or in `input` |
| **Max tokens param** | `max_completion_tokens` | `max_output_tokens` |
| **Tool results** | `role: "tool"`, `tool_call_id` | `type: "function_call_output"`, `call_id` |

Azure-specific differences from direct OpenAI:

| Aspect | OpenAI | Azure OpenAI |
|:---|:---|:---|
| **Auth header** | `Authorization: Bearer {key}` | `api-key: {key}` |
| **Endpoint** | `https://api.openai.com/v1/responses` | `https://{resource}.openai.azure.com/openai/v1/responses` |
| **Model field** | Model name (e.g., `gpt-5.4`) | Deployment name |

## User Review Required

> [!IMPORTANT]
> **Model selection**: The MODELS hash below includes common Azure-deployable OpenAI models. Since Azure uses deployment names (not model names) and the user can deploy any model, the MODELS list serves as a reference for cost estimation and context window tracking. Verify the models below match your actual Azure Foundry deployments.

> [!IMPORTANT]
> **Authentication**: Azure supports both API Key (`api-key` header) and Microsoft Entra ID (`Authorization: Bearer` header). This plan implements API Key authentication. Let me know if you need Entra ID/token-based auth as well.

## Open Questions

> [!IMPORTANT]
> **API Version**: The newer Azure `v1` API path (`/openai/v1/responses`) generally does not require an `api-version` query parameter. However, if your deployment needs a specific version, I can add an optional `api_version:` parameter to the constructor. Should I include it?

## Proposed Changes

### Backends Component

---

#### [NEW] `azure_foundry.rb`

New file at: `lib/boukensha/backends/azure_foundry.rb`

This backend will:
- Extend `Base` (like all other backends)
- Accept `api_key:`, `endpoint:`, and `model:` in the constructor
- Use the **Responses API** format for payloads (top-level `instructions`, `input` array, `max_output_tokens`)
- Use `api-key` header for Azure authentication
- Build the URL from the user's Azure endpoint

```ruby
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
        input << { role: "system", content: system } if system && !system.empty?

        messages.each do |msg|
          case msg.role
          when :tool_result
            input << {
              type: "function_call_output",
              call_id: msg.tool_use_id,
              output: msg.content
            }
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
            function: {
              name: tool.name,
              description: tool.description,
              parameters: {
                type: "object",
                properties: tool.parameters,
                required: tool.parameters.keys.map(&:to_s)
              }
            }
          }
        end
      end

      def to_payload(context, max_output_tokens: 1024)
        {
          model: @model,
          input: to_messages(context.system, context.messages),
          tools: to_tools(context.tools),
          max_output_tokens: max_output_tokens
        }
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
```

**Key design decisions:**

1. **`instructions` vs `input` for system prompt**: The Responses API supports both a top-level `instructions` field and `role: "system"` inside the `input` array. I'm using the `input` array approach to keep the `to_messages` method consistent with other backends that fold the system prompt into the message stream (OpenAI, Ollama, OllamaCloud). This also keeps the `to_payload` method simpler.

2. **Tool results use `function_call_output`**: The Responses API uses `type: "function_call_output"` with `call_id` (not `tool_call_id`) and `output` (not `content`) for tool results.

3. **`endpoint` parameter**: Azure requires a resource-specific URL. Rather than hardcoding, we accept the full base endpoint URL (e.g., `https://my-resource.openai.azure.com`), giving users flexibility.

4. **Model list mirrors OpenAI**: Since Azure deploys OpenAI models, the MODELS hash mirrors the existing OpenAI backend's models. Users reference their deployment name, which should match one of these model names.

---

### Main Entry Point

#### [MODIFY] `boukensha.rb`

Add the `require_relative` for the new backend:

```diff
 require_relative "boukensha/backends/openai"
+require_relative "boukensha/backends/azure_foundry"
```

---

### Example

#### [MODIFY] `example.rb`

Add an `azure_foundry` case to the provider switch:

```diff
 when "openai"
   Boukensha::Backends::OpenAI.new(api_key: ENV.fetch("OPENAI_API_KEY"), model: model)
+when "azure_foundry"
+  Boukensha::Backends::AzureFoundry.new(
+    api_key: ENV.fetch("AZURE_OPENAI_API_KEY"),
+    endpoint: ENV.fetch("AZURE_OPENAI_ENDPOINT"),
+    model: model
+  )
 when "gemini"
```

---

### Documentation

#### [MODIFY] `README.md`

Add a section documenting the new backend, consistent with existing backend documentation:

```diff
+### Boukensha::Backends::AzureFoundry
+
+Talks to `https://{resource}.openai.azure.com/openai/v1/responses` using the
+Responses API. Requires `AZURE_OPENAI_API_KEY` and `AZURE_OPENAI_ENDPOINT`
+environment variables. Supported models are listed in
+`Boukensha::Backends::AzureFoundry::MODELS`.
```

Also add `azure_foundry.rb` to the file table.

---

## Verification Plan

### Automated Tests

The project does not currently have a test suite. Verification will be done by running the example script.

```bash
cd /workspaces/claude-code-camp-2026-Q2/week1_baseline/ruby/03_prompt_builder

# 1. Verify Ruby can load all backends without errors
ruby -e "require_relative 'lib/boukensha'; puts 'All backends loaded OK'"

# 2. Verify the AzureFoundry backend can be instantiated and produces correct payload
ruby -e "
  require_relative 'lib/boukensha'
  require 'json'

  backend = Boukensha::Backends::AzureFoundry.new(
    api_key: 'test-key',
    endpoint: 'https://my-resource.openai.azure.com',
    model: 'gpt-5.4-mini'
  )

  ctx = Boukensha::Context.new(
    task: Boukensha::Tasks::Player,
    system: 'You are a test assistant.'
  )
  ctx.add_message(:user, 'Hello')
  ctx.add_message(:assistant, 'Hi there')
  ctx.add_message(:tool_result, 'Tool output', tool_use_id: 'call_123')

  builder = Boukensha::PromptBuilder.new(ctx, backend)
  payload = builder.to_api_payload

  # Verify Responses API structure
  raise 'Missing input key' unless payload[:input]
  raise 'Should not have messages key' if payload[:messages]
  raise 'Missing max_output_tokens' unless payload[:max_output_tokens]
  raise 'Wrong URL' unless builder.url == 'https://my-resource.openai.azure.com/openai/v1/responses'
  raise 'Missing api-key header' unless builder.headers['api-key'] == 'test-key'

  # Verify tool result format
  tool_result = payload[:input].find { |m| m[:type] == 'function_call_output' }
  raise 'Tool result missing call_id' unless tool_result[:call_id] == 'call_123'
  raise 'Tool result should use output not content' unless tool_result[:output] == 'Tool output'

  puts 'All AzureFoundry assertions passed!'
  puts JSON.pretty_generate(payload)
"
```

### Manual Verification

1. **Review the generated payload** output from the verification script to confirm it matches the Azure OpenAI Responses API format
2. **Verify the example script** runs with `provider: azure_foundry` in settings (requires actual Azure credentials)
3. **Check that existing backends still work** — the changes are additive only

## Revision Required

Test using [api client](../../../../week1_baseline/ruby/04_api_client/examples/example.rb) example is giving the following output:

```sh
=== BOUKENSHA Step 4: API Client ===

Config: #<Boukensha::Config dir=/workspaces/claude-code-camp-2026-Q2/.boukensha tasks=player>
Provider: azure_foundry
Model: gpt-5.4-mini
Sending request to https://claude-code-camp-resource.openai.azure.com/openai/v1/responses...

/workspaces/claude-code-camp-2026-Q2/week1_baseline/ruby/04_api_client/lib/boukensha/client.rb:62:in 'Boukensha::Client#call': API request failed after 1 attempt (400): { (Boukensha::ApiError)
  "error": {
    "message": "Missing required parameter: 'tools[0].name'.",
    "type": "invalid_request_error",
    "param": "tools[0].name",
    "code": "missing_required_parameter"
  }
}
        from examples/example.rb:82:in '<main>'
```

This seems to imply a malformed structure in the tool calling logic.

Consider the following course of action, but prioritize compatibility with the overall Boukensha implementation:

```txt
Summary of Changes Required in Boukensha::PromptBuilder
Link Tool Calls to Outputs: Ensure your prompt builder emits the assistant's function_call event in the assistant turn prior to emitting the function_call_output / tool output.

Assign Tool Roles: Format tool outputs as { "role": "tool", "tool_call_id": "...", "content": "..." }.

Move System Prompt: Either move the system prompt to top-level instructions or leave it as { "role": "developer" } inside input.
```

## Reviewed Implementation

### Root Cause Analysis

The `400` error `Missing required parameter: 'tools[0].name'` confirms the Responses API expects a **flat** tool schema where `name`, `description`, and `parameters` sit at the **top level** of each tool object — NOT nested inside a `function` wrapper. The original implementation used the Chat Completions nested format.

**Chat Completions API (what we had — wrong for Responses):**
```json
{
  "type": "function",
  "function": {
    "name": "read_file",
    "description": "...",
    "parameters": { ... }
  }
}
```

**Responses API (what we need — flat):**
```json
{
  "type": "function",
  "name": "read_file",
  "description": "...",
  "parameters": { ... }
}
```

The API sees `tools[0]` has `type` and `function` keys but no top-level `name`, hence the error.

### Additional Corrections

The revision notes also suggest two more changes to align with Responses API conventions:

1. **System prompt → `developer` role**: The Responses API designates `developer` as the modern replacement for `system`. Using `role: "developer"` inside `input` ensures the system prompt carries proper authority and future-compatibility with reasoning models.

2. **System prompt → `instructions` top-level field**: Alternatively, the system prompt can be passed as a top-level `instructions` string in the payload. This is the idiomatic Responses API approach and keeps the `input` array clean.

### Design Decision

We use the **top-level `instructions` field** for the system prompt. This is the cleanest approach for the Responses API:
- It's the recommended pattern for single-turn/stateless calls (which is how Boukensha works — full history each call).
- It keeps `input` focused on conversation items only.
- It avoids any ambiguity about `system` vs `developer` roles across different Azure model deployments.

### Compatibility with Boukensha

These changes are contained entirely within `AzureFoundry` — no changes to `PromptBuilder`, `Context`, or other backends are needed. The `to_payload` method receives `context` which carries `.system` and `.messages`, so we have full control over how to map them.

### Corrected Implementation

```ruby
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
```

### Summary of Changes vs Original

| Area | Original (broken) | Corrected |
|:---|:---|:---|
| **Tool schema** | Nested: `{ type: "function", function: { name: ..., ... } }` | Flat: `{ type: "function", name: ..., description: ..., parameters: ... }` |
| **System prompt** | Injected as `{ role: "system", content: ... }` into `input` array | Moved to top-level `instructions` field |
| **Input array** | Included system message as first item | Contains only conversation items (user/assistant/tool results) |
