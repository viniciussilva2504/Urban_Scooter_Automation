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
python -m pip install pytest selenium pillow imageio-ffmpeg
```

Instale e abra o Google Chrome. O Selenium Manager tenta localizar ou baixar um ChromeDriver compatível automaticamente.

Se o Selenium Manager não conseguir obter o driver, a fixture tenta usar a versão mais recente encontrada no cache do Selenium. Você também pode configurar `URBAN_CHROMEDRIVER` manualmente com um driver compatível com o Chrome instalado. Exemplo para esta máquina, se o arquivo ainda estiver presente:

```powershell
$env:URBAN_CHROMEDRIVER = "$env:USERPROFILE\.cache\selenium\chromedriver\win64\156.0.8078.80\chromedriver.exe"
```

### 3. Configure a estande de teste

Configure a URL da aplicação Web. O fixture mantém o idioma português mesmo quando a URL já contém `?lng=pt`:

```powershell
$env:URBAN_WEB_URL = "https://cnt-56ac29f0-0b53-460a-8a53-64bb249415e7.containerhub.tripleten-services.com?lng=pt"
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
- Um GIF animado e um vídeo MP4 em `reports/media/`, montados com capturas das etapas da interface (não é gravação contínua da tela).

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

Casos parametrizados aparecem como identificadores separados na coleta e são executados individualmente pelo loop. Os estados dos pedidos são preparados automaticamente pela suíte; se a estande estiver indisponível, o teste falha com o erro de conexão em vez de ser ignorado.

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

## Dados e resultados esperados

Os casos de status criam seus próprios pedidos na estande. Os cenários de aceite e chegada criam um entregador temporário pela API e o removem ao final, incluindo os pedidos associados. USBR31, USBR35 e USBR44 também criam pedidos. Use exclusivamente a estande de teste.

Alguns dados de validação têm defeitos já registrados na planilha: USBR13, USBR17, USBR21, USBR24 e USBR25. Esses parâmetros estão marcados como `XFAIL` enquanto a aplicação mantiver o comportamento reportado. `XFAIL` significa que a asserção do requisito falhou como previsto; `XPASS` indica que a aplicação pode ter sido corrigida e a marcação deve ser reavaliada. Isso mantém os defeitos visíveis sem contá-los como testes aprovados.

## Organização dos testes Web

- `tests/web/conftest.py`: fixtures do Chrome e configuração da URL.
- `tests/web/pages/urban_scooter_page.py`: Page Objects, locators, interações e waits explícitos.
- `tests/web/data.py`: URL da estande e dados reutilizados entre cenários.
- `tests/web/evidence.py`: captura checkpoints e gera GIF/MP4 por caso.
- `tests/web/scenarios/test_layout.py`: USBR1–USBR5.
- `tests/web/scenarios/test_order_form.py`: USBR6–USBR30 e USBR48.
- `tests/web/scenarios/test_order_flow.py`: USBR31–USBR38.
- `tests/web/scenarios/test_order_status.py`: USBR39–USBR47.
- `tests/web/README.md`: visão resumida da estrutura Web.

## API e Android

Os testes de API e Android estão em `tests/api/` e `tests/mobile/`, respectivamente. Eles não são executados pelos comandos Web acima. A URL-base atual da API é `https://cnt-56ac29f0-0b53-460a-8a53-64bb249415e7.containerhub.tripleten-services.com`; a documentação está em `https://cnt-56ac29f0-0b53-460a-8a53-64bb249415e7.containerhub.tripleten-services.com/docs/pt/`. Para executar a suíte de API, configure `URBAN_API_BASE_URL` com essa URL-base. Android requer Appium, UiAutomator2 e um dispositivo configurado. Consulte os respectivos arquivos `conftest.py` antes de executar essas suítes.
