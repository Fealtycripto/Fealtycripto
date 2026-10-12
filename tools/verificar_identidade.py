#!/usr/bin/env python3
"""Conferência manual, somente leitura, de fontes públicas explícitas. Sem rede/login."""
import argparse
import html
import json
import pathlib
import re
import tempfile
import unicodedata

def normalized(value):
    value = html.unescape(re.sub(r'<[^>]+>', ' ', value))
    value = ''.join(c for c in unicodedata.normalize('NFKD', value) if not unicodedata.combining(c))
    return re.sub(r'\s+', ' ', value).lower()

def check_data(data):
    errors = []
    expected = [('version', 'BIO-1.0'), ('person.name', 'Rony Costa (Zion)'),
                ('brand.name', 'CriptoZion'), ('brand.person_role', 'Fundador'),
                ('methodology.name', 'Zion Smart DCA'), ('methodology.person_role', 'Criador')]
    for field, value in expected:
        current = data
        for key in field.split('.'):
            current = current.get(key) if isinstance(current, dict) else None
        if current != value:
            errors.append(f'{field}: esperado {value!r}, encontrado {current!r}')
    if 'evolucao' not in normalized(data.get('methodology', {}).get('status', '')):
        errors.append('Zion Smart DCA deve ser identificada como em evolução')
    initiatives = {item.get('name'): item for item in data.get('independent_initiatives', [])}
    for name, role in [('DoubleDyn', 'Sócio'), ('Vila Pet Banho e Tosa', 'Empreendedor')]:
        item = initiatives.get(name, {})
        if item.get('person_role') != role:
            errors.append(f'{name}: função deve ser {role}')
        if 'independente' not in normalized(item.get('relationship_to_brand', '')):
            errors.append(f'{name}: associação deve permanecer independente')
    return errors

def check_text(text, required=()):
    value = normalized(text)
    errors = []
    for pattern in required:
        if not re.search(pattern, value):
            errors.append(f'fato essencial ausente: {pattern}')
    for pattern, message in [
        (r'rony\s+(?!costa\b)[a-z]+', 'nome de Rony divergente'),
        (r'(?:ceo|cto|co[- ]?fundador|fundador exclusivo)\s+(?:da|do|na)\s+doubledyn', 'função não aprovada na DoubleDyn'),
        (r'doubledyn\s*[-—:]\s*(?:ceo|cto|co[- ]?founder|co[- ]?fundador)', 'função não aprovada na DoubleDyn'),
        (r'doubledyn\s+(?:e\s+)?(?:parte|pertence|subsidiaria|empresa do|empresa da).{0,40}cripto\s*zion', 'associação indevida entre DoubleDyn e CriptoZion'),
        (r'(?:ceo|cto|co[- ]?founder)\s+rony costa', 'cargo não aprovado atribuído a Rony'),
    ]:
        if re.search(pattern, value):
            errors.append(message)
    return errors

def verify(manifest_path):
    manifest_path = pathlib.Path(manifest_path).resolve()
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    failures = []
    for source in manifest['sources']:
        path = (manifest_path.parent / source['path']).resolve()
        try:
            text = path.read_text(encoding='utf-8')
            if source.get('start'):
                text = text[text.index(source['start']):]
            if source.get('end'):
                text = text[:text.index(source['end'])]
            errors = check_data(json.loads(text)) if source.get('kind') == 'data' else check_text(text, source.get('required', []))
            failures.extend(f'{source["path"]}: {error}' for error in errors)
        except (OSError, ValueError, KeyError) as error:
            failures.append(f'{source["path"]}: {error}')
    return failures

def self_test(data_path):
    data = json.loads(pathlib.Path(data_path).read_text(encoding='utf-8'))
    with tempfile.TemporaryDirectory(prefix='bio-check-') as directory:
        root = pathlib.Path(directory)
        (root/'manifest.json').write_text(json.dumps({'sources': [{'path': 'copy.json', 'kind': 'data'}]}), encoding='utf-8')
        mutations = [('nome', lambda d: d['person'].update(name='Rony Silva (Zion)')),
                     ('funcao', lambda d: d['independent_initiatives'][0].update(person_role='CEO')),
                     ('associacao', lambda d: d['independent_initiatives'][0].update(relationship_to_brand='Empresa do CriptoZion')),
                     ('versao', lambda d: d.update(version='BIO-0.9'))]
        for name, mutate in mutations:
            copy = json.loads(json.dumps(data)); mutate(copy)
            (root/'copy.json').write_text(json.dumps(copy), encoding='utf-8')
            assert verify(root/'manifest.json'), f'Não detectou divergência de {name}'
        good = ['Rony Costa (Zion), conhecido como Fealty Crypto. Fundador do CriptoZion.',
                'CriptoZion: educação sobre Bitcoin e DeFi. Fundado por Rony Costa (Zion).',
                'Fealty Cripto / @0xFealty. Criador da Zion Smart DCA.',
                'Rony Costa é sócio da DoubleDyn, iniciativa independente do CriptoZion.']
        for text in good:
            assert not check_text(text), f'Rejeitou variação válida: {text}'
        for text in ['Rony Silva, fundador do CriptoZion.', 'Rony Costa é CEO da DoubleDyn.',
                     'DoubleDyn é parte do CriptoZion.', 'DoubleDyn — CTO']:
            assert check_text(text), f'Não detectou texto divergente: {text}'
    return 12

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=pathlib.Path, default=pathlib.Path(__file__).resolve().parents[1]/'identidade-fontes.json')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        count = self_test(pathlib.Path(__file__).resolve().parents[1]/'identidade-publica.json')
        print(f'Teste em cópias temporárias: {count} casos aprovados.')
    failures = verify(args.manifest)
    for failure in failures:
        print('ERRO:', failure)
    print('BIO-1.0: ' + ('divergências encontradas' if failures else 'fontes explícitas consistentes'))
    raise SystemExit(bool(failures))
