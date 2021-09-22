from typing import Dict, List, Tuple, Union
from requests import get
import sys
import pandas as pd
from pathlib import Path

base_dir = Path(__file__).parent.parent
base_url = 'https://delphi.cmu.edu/epidata'

def is_known_missing(source: str, signal: str) -> bool:
    if '7dav_cumulative' in signal:
        return True
    if source in ('youtube-survey', 'indicator-combination'):
        return True
    return False

def compute_missing_signals() -> List[Tuple[Tuple[str, str], Dict]]:
    defined_meta = get(f"{base_url}/covidcast/meta").json()
    defined_signals: Dict[Tuple[str, str], Dict] = {}
    for source in defined_meta:
        for signal in source['signals']:
            defined_signals[(signal['source'], signal['signal'])] = signal
            defined_signals[(source['db_source'], signal['signal'])] = signal

    computed_meta = get(f"{base_url}/covidcast_meta/?format=json").json()
    computed_signals: Dict[Tuple[str, str], List[Dict]] = {}
    for entry in computed_meta:
        computed_signals.setdefault((entry['data_source'], entry['signal']), []).append(entry)

    missing_signals: List[Tuple[Tuple[str, str], Dict]]  = []

    for key, infos in computed_signals.items():
        defined_info = defined_signals.get(key)
        if not defined_info:
            if not is_known_missing(key[0], key[1]):
                missing_signals.append((key, infos[0]))
    return missing_signals


def gen_row(source: str, signal: str, info: Dict) -> Dict:
    is_weighted = signal.startswith('smoothed_w') and not (signal.startswith('smoothed_wa') or signal.startswith('smoothed_we') or signal.startswith('smoothed_wi') or signal.startswith('smoothed_wo') or signal.startswith('smoothed_wu'))
    base_name = signal.replace('smoothed_w', 'smoothed_') if is_weighted else signal
    bool_str = lambda x: 'TRUE' if x else 'FALSE'

    return {
        'Source Subdivision': source,
        'Signal BaseName': base_name,
        'base_is_other': bool_str(False),
        'Signal': signal,
        'Compute From Base': False,
        'Name': "{base_name} (Weighted)" if is_weighted else signal,
        'Active': bool_str(True),
        'Short Description': 'TODO' if base_name == signal else '',
        'Description': 'TODO' if base_name == signal else '',
        'Time Type': info['time_type'],
        'Time Label': 'Week' if info['time_type'] == 'week' else 'Day',
        'Value Label': 'Percentage' if source == 'fb-survey' else 'Value',
        'Format': 'percent' if source == 'fb-survey' else 'raw',
        'Category': 'public' if source == 'fb-survey' else 'other',
        'High Values Are': 'neutral',
        'Is Smoothed': bool_str(signal.startswith('smoothed') or '7dav' in signal),
        'Is Weighted': bool_str(is_weighted),
        'Is Cumulative': bool_str('cumulative' in signal),
        'Has StdErr': 'TRUE' if source == 'fb-survey' else '',
        'Has Sample Size': 'TRUE' if source == 'fb-survey' else '',
        'Link': 'TODO'
    }

def generate_missing_info_hint(missing_signals: List[Tuple[Tuple[str, str], Dict]]) -> None:
    missing = pd.DataFrame.from_records([gen_row(s[0], s[1], info) for s, info in missing_signals])

    # use the current as base to have the right column order
    current = pd.read_csv(base_dir / 'src/server/endpoints/covidcast_utils/db_signals.csv')
    # clear
    current = current[0:0]
    guessed: pd.DataFrame = pd.concat([current, missing])
    guessed.to_csv(base_dir / 'missing_db_signals.csv', index=False)

missing = compute_missing_signals()
if missing:
    print(f'found {len(missing)} missing signals')
    generate_missing_info_hint(missing)
    sys.exit(1)
else:
    print(f'all signals found')
    sys.exit(0)

