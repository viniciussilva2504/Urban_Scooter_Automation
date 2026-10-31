# Suíte web

Os casos web estão separados por responsabilidade:

- `pages/urban_scooter_page.py`: locators, waits e ações dos Page Objects.
- `scenarios/test_layout.py`: USBR1–USBR5 (página inicial, cookies, accordion e ordem das seções).
- `scenarios/test_order_form.py`: USBR6–USBR30 e USBR48 (validação dos campos e seleção de estação).
- `scenarios/test_order_flow.py`: USBR31–USBR38 (pedido, data, período, opcionais e retorno entre etapas).
- `scenarios/test_order_status.py`: USBR39–USBR47 (consulta, cancelamento e estados de entrega).
- `data.py`: valores reutilizados nos cenários.
- `conftest.py`: configuração e isolamento do Chrome por teste.

Execute a suíte toda com `python -m pytest tests/web -v`, ou passe um arquivo ou nó pytest específico. Configure `URBAN_WEB_URL`; os cenários que precisam de pedidos existentes usam as variáveis de estado listadas no README da raiz. Os testes que criam pedidos usam apenas a estande de teste configurada.
