html = open('driftbound_flight_test.html','r',encoding='utf-8').read()

for token in ['sendMove', 'drawPlayerIndicator', '8766', 'lobbyConnect', 'ws_handler', 'MULTI_JS']:
    idx = html.find(token)
    print(f'{token}: {"found @" + str(idx) if idx>=0 else "MISSING"}')

# Check where the script tag ends vs where MULTI_JS should be
last_script = html.rfind('</script>')
print(f'\nlast </script> at: {last_script}')
print(f'last 400 chars of HTML:')
print(repr(html[-400:]))
