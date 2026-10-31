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

Execute a suíte toda com `python -m pytest tests/web -v`, ou passe um arquivo ou nó pytest específico. A URL atual da estande é usada por padrão e pode ser sobrescrita com `URBAN_WEB_URL`. Os casos de status preparam os pedidos e entregadores necessários pela interface/API de teste. Os resultados JUnit ficam em `reports/`; os vídeos e GIFs ficam em `reports/media/`.
