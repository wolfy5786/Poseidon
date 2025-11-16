/engine
   /core
       api_parser/           # Reads Swagger/OpenAPI
       test_generator/       # Calls AI to generate tests
       postman_adapter/      # Creates Postman collections dynamically
       reporter/             # Aggregates & formats results
       orchestrator/         # Coordinates the flow end-to-end
   /config
       engine.yaml           # Config for AI model, thresholds, envs
       test_schema.yaml      # Your custom test description schema
   /ci
       github_workflows/     # GitHub Actions pipeline
   /temp
       generated_tests/      # AI-generated YAML test files
       generated_collections/# Postman collections ready for execution
       results/              # Postman/Newman raw results
   /interfaces
       cli/                  # Command-line wrapper
       api/                  # (Optional) Engine REST API
   README.md
