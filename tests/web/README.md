# Suíte web

Os casos web estão separados por responsabilidade:

- `pages/urban_scooter_page.py`: locators, waits e ações dos Page Objects.
- `scenarios/test_layout.py`: USBR1–USBR5 (página inicial, cookies, accordion e ordem das seções).
- `scenarios/test_order_form.py`: USBR6–USBR30 e USBR48 (validação dos campos e seleção de estação).
- `scenarios/test_order_flow.py`: USBR31–USBR38 (pedido, data, período, opcionais e retorno entre etapas).
- `scenarios/test_order_status.py`: USBR39–USBR47 (consulta, cancelamento e estados de entrega).
- `data.py`: valores reutilizados nos cenários.
- `evidence.py`: checkpoints visuais convertidos em GIF e MP4 por teste.
- `conftest.py`: configuração e isolamento do Chrome por teste.

Com o ambiente virtual ativo, configure o estande e rode todos os casos individualmente no PowerShell:

```powershell
$env:URBAN_WEB_URL = "https://cnt-0e96eb19-5cee-43ab-8a26-f2506764625d.containerhub.tripleten-services.com/?lng=pt"
New-Item -ItemType Directory -Force reports | Out-Null
$nodes = python -m pytest --collect-only -q tests/web | Where-Object { $_ -match '^tests[\\/].+::test_' }
foreach ($node in $nodes) {
    $name = $node -replace '[^A-Za-z0-9_.-]', '_'
    Write-Host "Executando: $node"
    python -m pytest "$node" -v "--junitxml=reports/$name.xml" 2>&1 | Tee-Object "reports/$name.log"
}
```

Cada nó coletado é executado em uma chamada pytest separada; casos parametrizados também rodam separados. Para rodar apenas um caso, use o ID completo, por exemplo `python -m pytest "tests/web/scenarios/test_layout.py::test_cookie_consent_dismisses_banner" -v`. A URL padrão está em `data.py` e pode ser sobrescrita com `URBAN_WEB_URL`. Os casos de status preparam os pedidos e entregadores necessários pela interface/API de teste. Os resultados JUnit ficam em `reports/`; os vídeos e GIFs ficam em `reports/media/`.
