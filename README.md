# Urban Scooter — automação de QA

Este repositório reúne casos de teste Web, API e Android associados à planilha `Vinicius Silva_QA32_SPT9.xlsx`. **O passo a passo deste README cobre a suíte Web com Python, Selenium, pytest e Page Object Model (POM).** Os testes de API e Android têm pré-requisitos próprios e não fazem parte da execução descrita aqui.

## Suíte Web: instalação e execução

Os comandos abaixo usam Windows PowerShell. Execute-os a partir da pasta raiz do repositório.

### 1. Verifique o Python e crie o ambiente virtual

Confira se o Python está instalado:

```powershell
py --version
```

Crie o ambiente virtual uma vez. Se a pasta `.venv` já existir, pule a criação:

```powershell
py -m venv .venv
```

Ative o ambiente:

```powershell
.\.venv\Scripts\Activate.ps1
```

Quando ativo, o nome `.venv` aparece no início do prompt do PowerShell. Se a política de execução bloquear a ativação, libere scripts apenas para a janela atual e tente de novo:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Para sair do ambiente virtual ao terminar:

```powershell
deactivate
```

### 2. Instale as dependências Web

Com o ambiente virtual ativo, instale pytest e Selenium:

```powershell
python -m pip install --upgrade pip
python -m pip install pytest selenium
```

Instale e abra o Google Chrome. O Selenium Manager tenta localizar ou baixar um ChromeDriver compatível automaticamente.

Se o Selenium Manager não conseguir obter o driver, configure `URBAN_CHROMEDRIVER` com o caminho de um ChromeDriver compatível com a versão do Chrome instalado. Exemplo para esta máquina, se o arquivo ainda estiver presente:

```powershell
$env:URBAN_CHROMEDRIVER = "$env:USERPROFILE\.cache\selenium\chromedriver\win64\156.0.8078.80\chromedriver.exe"
```

### 3. Configure a estande de teste

Configure a URL da aplicação Web. O fixture mantém o idioma português mesmo quando a URL já contém `?lng=pt`:

```powershell
$env:URBAN_WEB_URL = "https://cnt-9b05c7d1-618d-4f8b-b030-b6b3cee639df?lng=pt"
```

Opcionalmente, execute o Chrome sem abrir uma janela:

```powershell
$env:URBAN_HEADLESS = "true"
```

### 4. Confira quais casos serão executados

Liste os casos que pytest encontrou, incluindo cada variação parametrizada:

```powershell
python -m pytest --collect-only -q tests/web
```

Um caso específico pode ser executado usando o identificador exibido nessa lista:

```powershell
python -m pytest "tests/web/scenarios/test_layout.py::test_cookie_consent_dismisses_banner" -v
```

Para ver os identificadores das variações de um teste parametrizado:

```powershell
python -m pytest --collect-only -q tests/web/scenarios/test_order_form.py
```

Copie o identificador completo desejado, incluindo o trecho entre colchetes, para executar somente aquela variação.

### 5. Execute todos os casos Web, um por vez, e documente os resultados

O script abaixo coleta os identificadores completos e chama pytest separadamente para cada caso. Cada execução gera:

- Um arquivo `.log` com a saída detalhada do terminal.
- Um arquivo `.xml` em formato JUnit com o resultado estruturado, duração, falha ou status de ignorado.

Os arquivos ficam na pasta `reports/`.

```powershell
New-Item -ItemType Directory -Force reports | Out-Null

$collectedTests = python -m pytest --collect-only -q tests/web
if ($LASTEXITCODE -ne 0) {
    throw "Falha ao coletar os testes Web. Confira as dependências e a saída acima."
}

$testNodes = $collectedTests | Where-Object { $_ -match '^tests[\\/].+::test_' }
if (-not $testNodes) {
    throw "Nenhum caso Web foi encontrado. Confira se o venv está ativo e as dependências instaladas."
}

$failedTests = @()
foreach ($testNode in $testNodes) {
    $reportName = $testNode -replace '[^A-Za-z0-9_.-]', '_'
    Write-Host "`nExecutando: $testNode"

    python -m pytest "$testNode" -v "--junitxml=reports/$reportName.xml" 2>&1 |
        Tee-Object -FilePath "reports/$reportName.log"

    if ($LASTEXITCODE -ne 0) {
        $failedTests += $testNode
    }
}

if ($failedTests.Count -gt 0) {
    Write-Host "`nCasos com falha:"
    $failedTests | ForEach-Object { Write-Host " - $_" }
    throw "A execução terminou com $($failedTests.Count) caso(s) com falha. Consulte reports/."
}

Write-Host "`nTodos os casos coletados terminaram sem falha. Consulte reports/ para logs e XMLs."
```

Casos parametrizados aparecem como identificadores separados na coleta e são executados individualmente pelo loop. Casos que dependem de dados ausentes podem terminar como `SKIPPED`; isso fica registrado no log e no XML.

### 6. Execute um arquivo inteiro ou a suíte toda em uma chamada

Para rodar cada grupo sem separar os casos individuais, use:

```powershell
python -m pytest tests/web/scenarios/test_layout.py -v --junitxml=reports/layout.xml
python -m pytest tests/web/scenarios/test_order_form.py -v --junitxml=reports/order-form.xml
python -m pytest tests/web/scenarios/test_order_flow.py -v --junitxml=reports/order-flow.xml
python -m pytest tests/web/scenarios/test_order_status.py -v --junitxml=reports/order-status.xml
```

Para rodar a suíte Web inteira em uma chamada:

```powershell
python -m pytest tests/web -v --junitxml=reports/web-suite.xml
```

## Dados necessários para testes de status

Os casos abaixo consultam pedidos já existentes. Se as variáveis não forem configuradas, os casos correspondentes serão ignorados pelo pytest:

```powershell
$env:URBAN_WEB_ORDER_ID = "<numero-de-rastreamento-existente>"
$env:URBAN_WEB_CANCEL_ORDER_ID = "<pedido-pendente-descartavel>"
$env:URBAN_WEB_ACCEPTED_ORDER_ID = "<pedido-aceito-pelo-entregador>"
$env:URBAN_WEB_INITIAL_ORDER_ID = "<pedido-no-deposito>"
$env:URBAN_WEB_EN_ROUTE_ORDER_ID = "<pedido-a-caminho>"
$env:URBAN_WEB_ARRIVED_ORDER_ID = "<pedido-entregue>"
```

Use números de rastreamento do ambiente de teste. O cenário de cancelamento modifica o pedido configurado em `URBAN_WEB_CANCEL_ORDER_ID`; escolha um pedido descartável. Os cenários USBR31, USBR35 e USBR44 criam pedidos na estande.

## Organização dos testes Web

- `tests/web/conftest.py`: fixtures do Chrome e configuração da URL.
- `tests/web/pages/urban_scooter_page.py`: Page Objects, locators, interações e waits explícitos.
- `tests/web/data.py`: dados reutilizados entre cenários.
- `tests/web/scenarios/test_layout.py`: USBR1–USBR5.
- `tests/web/scenarios/test_order_form.py`: USBR6–USBR30 e USBR48.
- `tests/web/scenarios/test_order_flow.py`: USBR31–USBR38.
- `tests/web/scenarios/test_order_status.py`: USBR39–USBR47.
- `tests/web/README.md`: visão resumida da estrutura Web.

## API e Android

Os testes de API e Android estão em `tests/api/` e `tests/mobile/`, respectivamente. Eles não são executados pelos comandos Web acima. A URL-base atual da API é `https://cnt-9b05c7d1-618d-4f8b-b030-b6b3cee639df`; a documentação está em `https://cnt-9b05c7d1-618d-4f8b-b030-b6b3cee639df/docs/pt/`. Para executar a suíte de API, configure `URBAN_API_BASE_URL` com essa URL-base. Android requer Appium, UiAutomator2 e um dispositivo configurado. Consulte os respectivos arquivos `conftest.py` antes de executar essas suítes.
