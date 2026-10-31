# Urban Scooter — automação de QA

O projeto reúne casos Web, Android e API relacionados à planilha `Vinicius Silva_QA32_SPT9.xlsx`. A automação de API cobre os casos API1–API31 com dados únicos e limpeza dos entregadores criados. Os testes de Web e Android ainda dependem de validação dos seletores e dos dados de ambiente descritos abaixo; a planilha não contém IDs de elementos nem credenciais para esses ambientes.

## 1. Preparar o ambiente virtual (Windows PowerShell)

Na raiz do projeto:

```powershell
py -0p                         # lista versões Python instaladas
py -3.10 -m venv .venv         # ou troque 3.10 pela versão disponível (3.10+)
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install pytest selenium Appium-Python-Client
```

Se a política do PowerShell bloquear a ativação, use o executável do venv diretamente em todos os comandos: `\.venv\Scripts\python.exe -m pytest ...`.

Para sair do ambiente: `deactivate`.

## 2. API (Python/pytest)

Configure `URBAN_API_BASE_URL` com a URL do servidor de **teste** (não use produção). O valor que estava no ambiente Postman foi `https://cnt-566b8697-3660-4522-9354-be62b138e876.containerhub.tripleten-services.com`; confirme que esse servidor continua disponível antes de executar.

```powershell
$env:URBAN_API_BASE_URL = "https://<servidor-de-teste>"
python -m pytest tests/api -v
```

Os casos criam entregadores com logins aleatórios e removem os registros após o uso. Se a conexão ou a URL não estiver configurada, pytest marca a suíte como ignorada. Para executar um caso ou grupo:

```powershell
python -m pytest tests/api/test_couriers.py::test_api1_create_courier_and_login -v
python -m pytest tests/api/test_couriers.py -k "invalid_login or password or first_name" -v
```

Também é possível executar a coleção manualmente no Postman, importando `postman/urban_scooter_env.json` e `postman/urban_scooter_api_collection.json`. Confira a variável `baseUrl` antes de iniciar.

## 3. Web (Python, Selenium, pytest e POM)

Defina `URBAN_WEB_URL` com a URL do ambiente de teste (não use produção). O Selenium Manager gerencia o ChromeDriver. Os testes usam waits explícitos de até 10 segundos e um navegador isolado por caso; não há `sleep` fixo nem espera implícita.

```powershell
$env:URBAN_WEB_URL = "https://cnt-a41adca0-cc6f-4d4c-844a-73cc747952be.containerhub.tripleten-services.com?lng=pt"
$env:URBAN_HEADLESS = "true"  # opcional
# Se o Selenium Manager não puder baixar o driver, aponte para um ChromeDriver compatível:
# $env:URBAN_CHROMEDRIVER = "C:\\WebDriver\\bin\\chromedriver.exe"
python -m pytest tests/web -v
```

Os Page Objects estão em `tests/web/pages/urban_scooter_page.py`, os cenários estão em `tests/web/scenarios/` e os dados reutilizáveis ficam em `tests/web/data.py`. Informe números de rastreamento para testar os estados específicos sem criar nem alterar esses pedidos:

```powershell
$env:URBAN_WEB_ORDER_ID = "<pedido-existente>"
$env:URBAN_WEB_CANCEL_ORDER_ID = "<pedido-pendente-descartável>"
$env:URBAN_WEB_ACCEPTED_ORDER_ID = "<pedido-aceito>"
$env:URBAN_WEB_INITIAL_ORDER_ID = "<pedido-no-depósito>"
$env:URBAN_WEB_EN_ROUTE_ORDER_ID = "<pedido-a-caminho>"
$env:URBAN_WEB_ARRIVED_ORDER_ID = "<pedido-entregue>"
```

Os casos de criação de pedidos usam dados válidos no ambiente de teste; o caso de cancelamento altera o pedido apontado por `URBAN_WEB_CANCEL_ORDER_ID`, que deve ser descartável. A aplicação atual não tem uma seção separada de regras de uso, então USBR5 verifica a ordem das seções existentes. A comparação visual do USBR3 com Figma requer uma referência de design, que não está incluída no repositório.

## 4. Android (Appium)

Pré-requisitos: Node.js, Appium 2 com driver UiAutomator2, Android SDK, emulador/dispositivo conectado e APK da aplicação. Instale o driver uma vez e confirme o pacote/atividade reais do APK:

```powershell
npm install --global appium
appium driver install uiautomator2
adb devices
```

Em um terminal, inicie o servidor:

```powershell
appium --address 127.0.0.1 --port 4723
```

Em outro terminal, ative o venv e execute:

```powershell
python -m pytest tests/mobile -v
python -m pytest tests/mobile/test_login.py -v
```

Antes, atualize `tests/mobile/conftest.py` com o `app_package`, `app_activity` e caminho do APK corretos. Os IDs `id_*` e os IDs sem prefixo `id_` divergem entre arquivos e foram presumidos; confira-os no Appium Inspector. Os casos de notificações, Figma, conectividade e fluxo de pedidos requerem dados/ações do backend e não devem ser considerados aprovados apenas por localizar um elemento.

## 5. Descobrir e selecionar testes

```powershell
python -m pytest --collect-only -q          # lista o que será coletado
python -m pytest tests/api -v                # somente API
python -m pytest tests/web -v                # somente Web
python -m pytest tests/mobile -v             # somente Android
```

Os testes móveis e web são testes de interface: dependem da aplicação e de ambiente em execução. Não há fixture que inicialize servidor/API ou crie os dados de pedidos necessários por conta própria.
