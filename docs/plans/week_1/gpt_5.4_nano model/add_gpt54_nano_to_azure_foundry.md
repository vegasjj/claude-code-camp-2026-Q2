# Add gpt-5.4-nano to Azure Foundry Backend

## Goal

Add the `gpt-5.4-nano` model to the `MODELS` constant in [`Boukensha::Backends::AzureFoundry`](file:///workspaces/claude-code-camp-2026-Q2/week1_baseline/ruby/12_context/lib/boukensha/backends/azure_foundry.rb). This model is already supported in the [`OpenAI` backend](file:///workspaces/claude-code-camp-2026-Q2/week1_baseline/ruby/12_context/lib/boukensha/backends/openai.rb#L28-L32) but is missing from the Azure Foundry backend, preventing users from deploying nano-tier models through Azure.

### Background

The `MODELS` hash in each backend serves as:
- A **validation allowlist** — [`Base.validate_model!`](file:///workspaces/claude-code-camp-2026-Q2/week1_baseline/ruby/12_context/lib/boukensha/backends/base.rb#L45-L51) rejects any model not present in the hash
- A **metadata registry** — providing `context_window`, `cost_per_million`, and `usage_unit` for cost estimation and context management

Currently the Azure Foundry backend supports 3 models while the OpenAI backend supports 4 (including `gpt-5.4-nano`). Since Azure deploys the same OpenAI models, the nano variant should be available in both backends.

## Proposed Changes

### Backends Component

---

#### [MODIFY] [`azure_foundry.rb`](file:///workspaces/claude-code-camp-2026-Q2/week1_baseline/ruby/12_context/lib/boukensha/backends/azure_foundry.rb)

Add a `"gpt-5.4-nano"` entry to the `MODELS` hash, placed after `"gpt-5.4-mini"` to maintain the descending cost order convention. The values are taken directly from the [OpenAI backend's nano entry](file:///workspaces/claude-code-camp-2026-Q2/week1_baseline/ruby/12_context/lib/boukensha/backends/openai.rb#L28-L32) to maintain consistency.

```diff
         "gpt-5.4-mini" => {
           context_window: 400_000,
           cost_per_million: { input: 0.75, output: 4.5 },
           usage_unit: :tokens
-        }
+        },
+        "gpt-5.4-nano" => {
+          context_window: 400_000,
+          cost_per_million: { input: 0.2, output: 1.25 },
+          usage_unit: :tokens
+        }
       }.freeze
```

> [!NOTE]
> No other files require changes. The `MODELS` hash is the single source of truth for model validation and metadata. The [`Base`](file:///workspaces/claude-code-camp-2026-Q2/week1_baseline/ruby/12_context/lib/boukensha/backends/base.rb) class, [`configure_model`](file:///workspaces/claude-code-camp-2026-Q2/week1_baseline/ruby/12_context/lib/boukensha/backends/base.rb#L86-L89), and all cost/context methods will automatically pick up the new entry.

## User Review Required

> [!IMPORTANT]
> **Pricing values**: The `cost_per_million` values (`input: 0.2`, `output: 1.25`) are taken from the existing OpenAI backend's `gpt-5.4-nano` entry. Azure pricing may differ from direct OpenAI pricing — please confirm these values match your Azure billing or adjust as needed.

> [!IMPORTANT]
> **Context window**: Set to `400_000` to match the OpenAI backend. Confirm this aligns with the Azure deployment's actual context limit.

## Verification Plan

### Automated Tests

```bash
cd /workspaces/claude-code-camp-2026-Q2/week1_baseline/ruby/12_context

# 1. Verify the module loads without errors
ruby -e "require_relative 'lib/boukensha'; puts 'All backends loaded OK'"

# 2. Verify gpt-5.4-nano is now accepted by AzureFoundry
ruby -e "
  require_relative 'lib/boukensha'
  backend = Boukensha::Backends::AzureFoundry.new(
    api_key: 'test-key',
    endpoint: 'https://test.openai.azure.com',
    model: 'gpt-5.4-nano'
  )
  raise 'Wrong model' unless backend.model == 'gpt-5.4-nano'
  raise 'Wrong context_window' unless backend.context_window == 400_000
  raise 'Wrong input cost' unless backend.input_token_cost_per_million == 0.2
  raise 'Wrong output cost' unless backend.output_token_cost_per_million == 1.25
  raise 'Wrong usage_unit' unless backend.usage_unit == :tokens
  puts 'gpt-5.4-nano: all assertions passed!'
"

# 3. Verify existing models still work
ruby -e "
  require_relative 'lib/boukensha'
  %w[gpt-5.5 gpt-5.4 gpt-5.4-mini].each do |m|
    Boukensha::Backends::AzureFoundry.new(
      api_key: 'test-key',
      endpoint: 'https://test.openai.azure.com',
      model: m
    )
    puts \"#{m}: OK\"
  end
  puts 'All existing models still work!'
"
```

### Manual Verification

1. Confirm the diff is a clean 5-line addition with no other changes
2. Verify the model entry structure matches the other entries in the hash (same keys, same types)
