# Azure Foundry Backend implementation

## Goal

Support for a new backend is needed on [backends](../../../../week1_baseline/ruby/03_prompt_builder/lib/boukensha/backends/) so that using Azure Foundry deployments is possible (specifically openai models).

Following structure with [base.rb](../../../../week1_baseline/ruby/03_prompt_builder/lib/boukensha/backends/base.rb) and compatibility with [prompt_builder.rb](../../../../week1_baseline/ruby/03_prompt_builder/lib/boukensha/prompt_builder.rb) is required to avoid unnecessary changes to the rest of the code.

The **responses API** should be used to interact with the models instead of the older **chat completions API** when creating the backend as this is the new structure going forward.
