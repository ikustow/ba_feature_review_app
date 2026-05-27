# Project 3. Development Plan: AI Feature Review ChatGPT App

## Цель документа

Этот документ - пошаговый план разработки MVP для **AI Feature Review ChatGPT App** на базе `docs/raw_data`.

Главное решение по архитектуре:

```text
ChatGPT = reasoning layer
MCP/backend = deterministic data access, OpenAPI slicing, traceability, rule checks
Widget = Feature Review Workspace with a visual UML Feature Flow view
```

В MVP нет backend AI, LangChain, LangGraph, редактирования документации, apply changes или GitHub PR creation. Backend только готовит надежный structured context, а ChatGPT объясняет выводы пользователю.

## MVP Definition

MVP считается готовым, если пользователь может:

1. Открыть ChatGPT App.
2. Увидеть список features из `docs/raw_data/synthetic_product_docs/manifest.json`.
3. Выбрать feature или написать в чат: `Проверь Pet Lifecycle Management`.
4. Получить feature context:
   - user story;
   - acceptance criteria;
   - related incidents;
   - related PlantUML diagrams;
   - только релевантные OpenAPI operations;
   - related schemas;
   - deterministic findings.
5. Увидеть Feature Review Workspace в widget, включая красиво отрендеренную UML-диаграмму feature flow.
6. Попросить ChatGPT объяснить gaps, missing tests и stakeholder questions на основе structured tool outputs.

## Принципы разработки

- **Read-only first:** MVP ничего не меняет в исходных файлах.
- **No backend AI:** backend не вызывает отдельную AI-модель.
- **Small OpenAPI context:** не отправлять весь `openapi.yaml`, только operation-level slices.
- **Visual feature flow:** UML diagrams являются core feature, а не decoration.
- **Diagram/API linking:** diagram steps должны ссылаться на `operationId`, где это возможно.
- **Evidence-first:** каждое finding должно ссылаться на document id, operation id или schema.
- **One user intent per tool:** MCP tools должны быть маленькими и понятными.
- **Widget is for navigation:** reasoning остается в ChatGPT conversation, widget показывает structured review.
- **Tests before polish:** сначала парсинг, slicing и rule checks, потом визуальная доработка.

## Phase 0. Подготовка проекта

### Задачи

1. Зафиксировать целевую структуру репозитория.
2. Выбрать package manager для frontend/MCP server: `pnpm`.
3. Выбрать Python tooling для backend: `uv`.
4. Создать базовые `.env.example` и README placeholders.
5. Убедиться, что `docs/raw_data` остается source dataset для MVP.
6. Добавить целевую папку для diagrams в raw data.

### Целевая структура

```text
ba_feature_review_app/
  apps/
    mcp-server/
    widget/
  services/
    review-service/
  docs/
    raw_data/
      synthetic_product_docs/
        diagrams/
    project_3_ai_business_analyst_copilot.md
    project_3_feature_review_app_development_plan.md
```

### Done

- Есть monorepo skeleton.
- `docs/raw_data` не перемещен и не изменен.
- В raw data запланирована папка `synthetic_product_docs/diagrams`.
- README объясняет, что MVP read-only.

## Phase 1. Backend data loading

### Цель

Научить backend читать manifest и markdown product docs.

### Задачи

1. Создать `services/review-service`.
2. Добавить Pydantic models:
   - `ProductDoc`;
   - `FeatureSummary`;
   - `FeatureContext`;
   - `OpenAPIOperationSlice`;
   - `FeatureDiagram`;
   - `DiagramStep`;
   - `RuleFinding`;
   - `TestIdea`;
   - `FeatureAuditResult`.
3. Реализовать `manifest_loader.py`.
4. Реализовать `markdown_loader.py`:
   - parse YAML frontmatter;
   - extract title;
   - keep body text;
   - preserve document id, artifact type, domain, version.
5. Реализовать `feature_catalog.py`:
   - user story становится primary feature;
   - AC подтягивается через `related_user_story`;
   - incidents подтягиваются по пересечению related operations и domain.
6. Расширить manifest model под `related_diagrams`.
7. Добавить diagram entries в manifest:
   - `diag_pet_lifecycle_sequence_v1`;
   - `diag_store_order_checkout_sequence_v1`;
   - `diag_user_account_access_sequence_v1`;
   - `diag_pet_image_upload_sequence_v1`.

### Проверки

```bash
uv run pytest tests/test_manifest_loader.py
uv run pytest tests/test_markdown_loader.py
uv run pytest tests/test_feature_catalog.py
```

### Done

- Backend возвращает 4 features:
  - Pet Lifecycle Management;
  - Store Order Checkout;
  - User Account Access;
  - Pet Image Upload.
- Для каждой feature известны user story, AC, related operations, related diagrams и incidents.

## Phase 2. OpenAPI parser and slicer

### Цель

Научить backend доставать из одного `openapi.yaml` только endpoints, относящиеся к feature.

### Задачи

1. Реализовать `openapi/parser.py`.
2. Реализовать `openapi/operation_index.py`.
3. Индексировать операции по:
   - `operationId`;
   - method + path;
   - tag;
   - schema refs.
4. Реализовать `openapi/slicer.py`.
5. Для списка `related_openapi_operations` возвращать:
   - method;
   - path;
   - operationId;
   - summary;
   - parameters;
   - requestBody;
   - responses;
   - security;
   - tags.
6. Реализовать `openapi/schema_resolver.py`.
7. Подтягивать только schemas, реально используемые в selected operations.
8. Добавить depth limit для nested `$ref`.

### Пример

Для `us_pet_lifecycle_management_v1` вернуть:

```text
POST /pet              addPet
PUT /pet               updatePet
GET /pet/{petId}       getPetById
GET /pet/findByStatus  findPetsByStatus
DELETE /pet/{petId}    deletePet
```

Не возвращать весь `openapi.yaml`.

### Проверки

```bash
uv run pytest tests/test_openapi_operation_index.py
uv run pytest tests/test_openapi_slicer.py
```

### Done

- `get_feature_context` может включить OpenAPI slice.
- Unit tests доказывают, что для feature возвращаются только related operations.
- Unit tests доказывают, что `components` не возвращается целиком.

## Phase 3. PlantUML diagrams and rendering

### Цель

Добавить feature-level UML diagrams как одну из core capabilities приложения.

### Raw data

Создать:

```text
docs/raw_data/synthetic_product_docs/diagrams/
  pet_lifecycle_sequence.puml
  store_order_checkout_sequence.puml
  user_account_access_sequence.puml
  pet_image_upload_sequence.puml
```

Каждая диаграмма должна быть PlantUML sequence diagram и содержать operation markers:

```plantuml
' operationId: findPetsByStatus
```

### Задачи

1. Реализовать `data/diagram_loader.py`.
2. Реализовать `diagrams/plantuml_parser.py`:
   - extract title;
   - extract participants;
   - extract steps;
   - extract `operationId` comments.
3. Реализовать `diagrams/renderer.py`:
   - render `.puml` to SVG;
   - or load pre-rendered SVG from cache.
4. Реализовать `diagrams/step_mapper.py`:
   - map diagram steps to OpenAPI operation IDs;
   - preserve source line numbers.
5. Добавить diagram data в `FeatureContext`.
6. Добавить tests для diagram loading and mapping.

### Проверки

```bash
uv run pytest tests/test_diagram_loader.py
uv run pytest tests/test_plantuml_parser.py
uv run pytest tests/test_diagram_operation_mapping.py
```

### Done

- Для каждой feature есть related diagram.
- Backend может вернуть PlantUML source.
- Backend может вернуть rendered SVG или SVG cache path.
- Diagram steps связаны с operation IDs там, где есть markers.

## Phase 4. Deterministic rule checks

### Цель

Сделать первый набор rule-based findings без AI.

### Checks

1. **Operation coverage**
   - Все операции из manifest существуют в OpenAPI.

2. **AC operation coverage**
   - Операции из user story упомянуты в acceptance criteria.

3. **Response coverage**
   - Error responses вроде `400`, `404`, `422` отражены в AC или test ideas.

4. **Schema required fields**
   - Required fields из schema упомянуты в story/AC.

5. **Enum rules**
   - Enum values из OpenAPI отражены в product rules или AC.

6. **Security coverage**
   - Secured operations имеют auth/authorization expectations в docs.

7. **Diagram operation coverage**
   - Key operations from feature manifest appear in related UML diagram.

8. **Diagram-only behavior**
   - Diagram does not describe behavior absent from OpenAPI/docs.

9. **Diagram incident coverage**
   - Incident-affected operations appear in the feature flow when relevant.

10. **Incident regression coverage**
   - Incident resolution notes превращаются в regression test ideas.

11. **Open questions**
   - Open questions из docs поднимаются в review output.

### Задачи

1. Создать модуль `checks/`.
2. Каждый check реализовать отдельной функцией.
3. Все findings возвращать как `RuleFinding`.
4. Для каждого finding сохранять:
   - severity;
   - category;
   - title;
   - description;
   - evidence refs;
   - affected operation ids;
   - recommended action.

### Проверки

```bash
uv run pytest tests/test_rule_checks.py
uv run pytest tests/test_diagram_consistency_checks.py
```

### Done

- Для `Pet Lifecycle Management` находится finding про regression test для `updatePet` -> `findPetsByStatus`.
- Для `Pet Lifecycle Management` diagram содержит markers для ключевых operations.
- Для `User Account Access` находится finding по login/header/session expectations.
- Для `Store Order Checkout` находится finding по order id boundary или error response coverage.

## Phase 5. Review-service API

### Цель

Поднять FastAPI backend, который будет вызывать MCP server.

### Endpoints

```text
GET /health
GET /features
GET /features/{feature_id}
GET /features/{feature_id}/diagrams
GET /diagrams/{diagram_id}
GET /openapi/operations/{operation_id}
POST /features/{feature_id}/audit
POST /features/{feature_id}/diagram-audit
POST /incidents/{incident_id}/impact
POST /features/{feature_id}/test-gaps
```

### Задачи

1. Реализовать `api/main.py`.
2. Реализовать `api/routes.py`.
3. Добавить config для paths:
   - `RAW_DATA_DIR`;
   - `OPENAPI_PATH`;
   - `MANIFEST_PATH`.
4. Добавить config/cache для rendered diagrams.
5. Сделать response models Pydantic.
6. Добавить simple in-memory cache для parsed manifest/OpenAPI/diagrams.

### Проверки

```bash
uv run uvicorn feature_review.api.main:app --reload --port 8000
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/features
```

### Done

- API возвращает list of features.
- API возвращает feature context с OpenAPI slice и related diagrams.
- API возвращает diagram source/rendered SVG.
- API возвращает audit result с deterministic findings.

## Phase 6. MCP server

### Цель

Сделать Apps SDK/MCP layer, через который ChatGPT вызывает backend.

### Tools

1. `list_features`
2. `get_feature_context`
3. `get_openapi_operation`
4. `get_feature_diagrams`
5. `get_diagram`
6. `audit_feature_consistency`
7. `audit_diagram_consistency`
8. `analyze_incident_impact`
9. `generate_test_gap_report`
10. `render_feature_review_workspace`
11. `search`
12. `fetch`

### Задачи

1. Создать `apps/mcp-server`.
2. Настроить TypeScript.
3. Добавить HTTP transport и `/mcp`.
4. Сделать `review_service_client.ts`.
5. Описать Zod schemas для input/output tools.
6. Для всех tools поставить `readOnlyHint: true`, кроме render tool where applicable.
7. Реализовать standard `search` and `fetch` compatibility:
   - `search(query)` возвращает one text content item with JSON string;
   - `fetch(id)` возвращает full text and metadata.
8. Зарегистрировать widget resource:
   - `ui://widget/feature-review-workspace-v1.html`;
   - MIME type `text/html;profile=mcp-app`;
   - CSP metadata.

### Проверки

```bash
pnpm --filter mcp-server test
pnpm --filter mcp-server dev
```

### Done

- MCP server exposes `/mcp`.
- Tool descriptors are visible in MCP inspector or ChatGPT Developer Mode.
- Diagram tools return source and SVG without mutating files.
- `search` and `fetch` pass contract tests.
- Tools return compact structuredContent.
- Larger widget payload goes in `_meta`.

## Phase 7. Widget: Feature Review Workspace

### Цель

Сделать UI, где пользователь может выбрать feature и изучить review.

### Views

1. **Features**
   - feature list;
   - domain;
   - related operations count;
   - incident count.

2. **Overview**
   - status;
   - summary cards;
   - top findings;
   - next actions.

3. **Docs**
   - user story;
   - acceptance criteria;
   - important product rules.

4. **OpenAPI**
   - operation table;
   - method/path;
   - parameters;
   - responses;
   - related schemas.

5. **Diagram**
   - rendered PlantUML SVG;
   - zoom/pan;
   - step list;
   - source toggle;
   - operation highlighting;
   - warnings for diagram/API drift.

6. **Incidents**
   - incident notes;
   - affected operations;
   - suspected root cause;
   - resolution notes.

7. **Consistency**
   - deterministic findings;
   - severity;
   - evidence;
   - recommended action.

8. **Test gaps**
   - missing tests;
   - regression tests;
   - contract tests.

9. **Traceability**
   - user story -> AC -> diagram step -> operationId -> incident -> test idea.

10. **Source**
   - raw markdown;
   - PlantUML source;
   - compact OpenAPI slice.

### Задачи

1. Создать `apps/widget`.
2. Настроить Vite + React + TypeScript.
3. Реализовать bridge helpers:
   - `use_tool_result`;
   - `use_call_tool`;
   - `use_widget_state`.
4. Реализовать `FeatureList`.
5. Реализовать selected feature state.
6. Реализовать tab navigation.
7. Реализовать `DiagramCanvas` для SVG rendering.
8. Реализовать `DiagramStepList` и operation highlighting.
9. Реализовать tables/panels для OpenAPI operations and findings.
10. Добавить empty/loading/error states.
11. Добавить `Ask ChatGPT about this finding` action:
   - selected finding попадает в model-visible context or follow-up message.

### Проверки

```bash
pnpm --filter widget build
pnpm --filter widget test
```

### Done

- Widget показывает list of features.
- Click на feature загружает context.
- Widget красиво рендерит related UML diagram.
- Widget показывает OpenAPI slice, а не весь spec.
- Findings читаемы и связаны с evidence.

## Phase 8. Local ChatGPT integration and chat-first validation

### Цель

Подключить локальный MCP server к ChatGPT Developer Mode и проверить оба пользовательских режима:

- app-first: пользователь выбирает feature в widget;
- chat-first: пользователь пишет запрос в чат, а ChatGPT сам вызывает tools.

Chat-first flow нельзя полноценно считать готовым до реального подключения к ChatGPT, поэтому integration и validation идут одной фазой.

### Local integration steps

1. Start review service:

```bash
cd services/review-service
uv run uvicorn feature_review.api.main:app --reload --port 8000
```

2. Start MCP server:

```bash
cd apps/mcp-server
pnpm dev
```

3. Expose MCP server:

```bash
ngrok http 2091
```

4. In ChatGPT:

```text
Settings -> Apps & Connectors -> Advanced settings -> Developer Mode
Create app/connector
URL: https://<subdomain>.ngrok.app/mcp
```

5. Refresh app metadata after tool/schema/resource changes.

### Demo prompts

```text
Проверь Pet Lifecycle Management. Совпадают ли user story, AC и OpenAPI?
```

```text
Что не так вокруг findPetsByStatus?
```

```text
Что incident Pet Status Filter Mismatch говорит нам про missing tests?
```

```text
Собери QA gap report по Store Order Checkout.
```

```text
Покажи flow diagram по Pet Lifecycle Management и объясни, какие API операции на нем есть.
```

### Ожидаемое поведение ChatGPT

Для `Проверь Pet Lifecycle Management`:

```text
1. list_features
2. get_feature_context
3. get_feature_diagrams
4. audit_feature_consistency
5. audit_diagram_consistency
6. render_feature_review_workspace
7. concise explanation in chat
```

### Done

- ChatGPT выбирает правильную feature по названию.
- Если feature name ambiguous, ChatGPT уточняет.
- ChatGPT объясняет findings, но не выдумывает endpoints.
- ChatGPT может ссылаться на diagram steps and operation IDs.
- ChatGPT указывает widget как место для деталей.
- ChatGPT sees tools.
- ChatGPT can call `list_features`.
- ChatGPT can render widget.
- Chat-first demo prompt works.

## Phase 9. Testing strategy

### Backend tests

- manifest loading;
- markdown frontmatter parsing;
- feature catalog linking;
- diagram loading;
- PlantUML parsing;
- diagram rendering/cache;
- diagram step -> operationId mapping;
- OpenAPI operation index;
- OpenAPI slicing;
- schema ref resolution;
- rule checks;
- diagram consistency checks;
- API response contracts.

### MCP tests

- tool descriptors;
- input/output schemas;
- `search`/`fetch` standard contract;
- render tool metadata;
- diagram tool outputs;
- backend client error handling.

### Widget tests

- renders feature list;
- renders selected feature;
- renders UML diagram SVG;
- highlights operation from diagram step;
- renders OpenAPI operations;
- renders findings;
- handles empty/loading/error states.

### Manual tests

- Chat-first prompt;
- app-first feature selection;
- operation-level question;
- diagram flow question;
- incident impact question;
- QA gap report question.

## Phase 10. Documentation and portfolio artifacts

### Документы

1. `README.md`
   - what the app does;
   - setup;
   - demo prompts;
   - architecture;
   - limitations.

2. `docs/architecture.md`
   - ChatGPT -> MCP -> backend -> widget flow.

3. `docs/openapi_slicing_strategy.md`
   - operation index;
   - schema resolver;
   - examples.

4. `docs/diagram_rendering_strategy.md`
   - PlantUML format;
   - operation markers;
   - SVG rendering/cache;
   - widget interactions.

5. `docs/feature_review_examples.md`
   - Pet Lifecycle review;
   - incident impact review;
   - QA gap report.

6. `docs/eval_methodology.md`
   - expected properties;
   - metrics;
   - no invented results.

### Portfolio demo

Minimal demo script:

```text
1. Open ChatGPT App.
2. Show feature list.
3. Select Pet Lifecycle Management.
4. Show rendered UML Feature Flow diagram.
5. Click diagram step and highlight related OpenAPI endpoint.
6. Show related OpenAPI endpoints.
7. Show incident-linked regression gap.
8. Ask ChatGPT: "What tests are missing?"
9. Show concise answer + widget evidence.
```

## Final MVP checklist

- [ ] `list_features` returns 4 features.
- [ ] Raw data contains 4 PlantUML feature diagrams.
- [ ] Manifest links features to diagram IDs.
- [ ] `get_feature_context` returns user story, AC, incidents, diagrams and OpenAPI slice.
- [ ] `get_feature_diagrams` returns source and rendered SVG.
- [ ] OpenAPI slicer does not return full `openapi.yaml`.
- [ ] Diagram parser maps operation markers to operation IDs.
- [ ] `audit_feature_consistency` returns deterministic findings.
- [ ] `audit_diagram_consistency` returns diagram/API findings.
- [ ] `search` and `fetch` follow standard compatibility shape.
- [ ] Widget renders feature list.
- [ ] Widget renders selected feature context.
- [ ] Widget renders UML diagram view.
- [ ] Widget supports diagram step -> operation highlighting.
- [ ] Widget renders OpenAPI operation table.
- [ ] Widget renders findings with evidence.
- [ ] Chat-first flow works for Pet Lifecycle Management.
- [ ] App-first flow works from feature list.
- [ ] Tests cover parsing, slicing and rule checks.
- [ ] README has local setup and demo prompts.
- [ ] Docs clearly state MVP is read-only and backend has no AI layer.

## Suggested build order

If time is limited, build in this exact order:

1. Backend manifest loader.
2. Backend OpenAPI operation index.
3. Add PlantUML raw diagrams and manifest links.
4. Backend diagram loader/parser.
5. Backend feature context endpoint.
6. Deterministic checks.
7. Diagram consistency checks.
8. MCP `list_features`.
9. MCP `get_feature_context`.
10. MCP `get_feature_diagrams`.
11. MCP `audit_feature_consistency`.
12. Minimal widget with feature list and overview.
13. Diagram tab.
14. OpenAPI tab.
15. Findings tab.
16. ChatGPT Developer Mode test.
17. README and demo docs.

This order gives visible progress early and avoids spending time on widget polish before the data contract is stable.
