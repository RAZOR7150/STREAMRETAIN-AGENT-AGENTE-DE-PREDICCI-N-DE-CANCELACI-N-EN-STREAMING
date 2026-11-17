"""Auditoría de los CSV locales de recomendación KKBox, con biblioteca estándar.

No modifica los datos ni entrena modelos. Recorre todas las filas, no una muestra.
"""
import csv
import hashlib
import json
import math
from collections import Counter
from datetime import datetime
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'kkbox-music-recommendation-challenge'
OUT = ROOT / 'docs' / 'auditoria_datos_kkbox.json'
ORDER = ['members.csv', 'songs.csv', 'song_extra_info.csv', 'train.csv',
         'test.csv', 'sample_submission.csv']
NUMERIC = {'bd', 'song_length', 'id', 'target'}
CATEGORICAL = {'city', 'gender', 'registered_via', 'language', 'target',
               'source_system_tab', 'source_screen_name', 'source_type'}
DATES = {'registration_init_time', 'expiration_date'}


def run():
    start = time.monotonic()
    report = {
        'review_date': '2026-11-15',
        'scope': 'Todos los registros CSV; solo lectura; sin entrenamiento',
        'dataset': 'KKBox Music Recommendation Challenge',
        'fit_for_subscription_churn': False,
        'label_meaning_from_local_description': 'Reescucha de una canción dentro de un mes del primer evento observable; no abandono',
        'limitations': ['No se verificaron duplicados exactos de filas completas ni pares usuario-canción repetidos.',
                       'Vacío significa cadena vacía; no se imputaron otros códigos como nulos.',
                       'No se verificaron integridad de archivos 7z ni licencia de recomendación.',
                       'Fechas de eventos de escucha ausentes del esquema; no se infiere el orden temporal de las filas.'],
        'files': {},
    }
    members, songs, extra = set(), set(), set()
    train_users, train_songs = set(), set()
    for filename in ORDER:
        path = DATA / filename
        sha = hashlib.sha256()
        with path.open('rb') as f:
            for chunk in iter(lambda: f.read(4 * 1024 * 1024), b''):
                sha.update(chunk)
        info = {'path': path.relative_to(ROOT).as_posix(), 'bytes': path.stat().st_size,
                'sha256': sha.hexdigest(), 'rows': 0, 'malformed_rows': 0,
                'empty': Counter(), 'categories': {}, 'numeric': {}, 'dates': {},
                'checks': Counter()}
        users, used_songs = set(), set()
        pk = members if filename == 'members.csv' else songs if filename == 'songs.csv' else extra if filename == 'song_extra_info.csv' else None
        with path.open(encoding='utf-8-sig', newline='') as f:
            reader = csv.reader(f)
            columns = next(reader)
            info['columns'] = columns
            info['empty'].update({c: 0 for c in columns})
            info['categories'] = {c: Counter() for c in columns if c in CATEGORICAL}
            info['numeric'] = {c: {'min': None, 'max': None, 'negative': 0, 'zero': 0, 'invalid': 0} for c in columns if c in NUMERIC}
            info['dates'] = {c: {'min': None, 'max': None, 'invalid': 0} for c in columns if c in DATES}
            for row in reader:
                info['rows'] += 1
                if len(row) != len(columns):
                    info['malformed_rows'] += 1
                    continue
                values = dict(zip(columns, row))
                for c, value in values.items():
                    if value == '':
                        info['empty'][c] += 1
                        continue
                    if c in info['categories']:
                        info['categories'][c][value] += 1
                    if c in info['numeric']:
                        st = info['numeric'][c]
                        try:
                            number = float(value)
                            if not math.isfinite(number):
                                raise ValueError()
                            st['min'] = number if st['min'] is None else min(st['min'], number)
                            st['max'] = number if st['max'] is None else max(st['max'], number)
                            st['negative'] += number < 0
                            st['zero'] += number == 0
                        except ValueError:
                            st['invalid'] += 1
                    if c in info['dates']:
                        st = info['dates'][c]
                        try:
                            parsed = datetime.strptime(value, '%Y%m%d').date().isoformat()
                            st['min'] = parsed if st['min'] is None else min(st['min'], parsed)
                            st['max'] = parsed if st['max'] is None else max(st['max'], parsed)
                        except ValueError:
                            st['invalid'] += 1
                if pk is not None:
                    key = row[0]
                    info['checks']['duplicate_primary_key_rows'] += key in pk
                    pk.add(key)
                if filename == 'members.csv':
                    try:
                        age = int(values['bd'])
                        info['checks']['age_below_0_or_above_100'] += age < 0 or age > 100
                        info['checks']['age_between_1_and_9'] += 0 < age < 10
                    except ValueError:
                        pass
                    info['checks']['expiration_before_registration'] += values['expiration_date'] < values['registration_init_time']
                if filename in ('train.csv', 'test.csv'):
                    user, song = values['msno'], values['song_id']
                    users.add(user)
                    used_songs.add(song)
                    info['checks']['rows_user_missing_members'] += user not in members
                    info['checks']['rows_song_missing_songs'] += song not in songs
                    info['checks']['rows_song_missing_extra_info'] += song not in extra
                if 'id' in values:
                    info['checks']['id_not_equal_zero_based_row_number'] += values['id'] != str(info['rows'] - 1)
        if pk is not None:
            info['unique_primary_keys'] = len(pk)
        if filename in ('train.csv', 'test.csv'):
            info['unique_users'] = len(users)
            info['unique_songs'] = len(used_songs)
            info['unique_users_missing_members'] = len(users - members)
            info['unique_songs_missing_songs'] = len(used_songs - songs)
            info['unique_songs_missing_extra_info'] = len(used_songs - extra)
            if filename == 'train.csv':
                train_users, train_songs = users, used_songs
            else:
                info['users_also_in_train'] = len(users & train_users)
                info['songs_also_in_train'] = len(used_songs & train_songs)
        if filename == 'song_extra_info.csv':
            info['keys_also_in_songs'] = len(extra & songs)
        report['files'][filename] = info
        OUT.parent.mkdir(exist_ok=True)
        OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'{filename}: {info["rows"]:,} filas revisadas', flush=True)
    report['elapsed_seconds'] = round(time.monotonic() - start, 2)
    report['complete'] = True
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Auditoría completa:', OUT, flush=True)


if __name__ == '__main__':
    run()
