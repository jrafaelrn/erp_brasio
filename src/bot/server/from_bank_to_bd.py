import from_bank_sicredi
from datetime import datetime


def download_all(downloads_day, import_bd=False): 

    # Sig-in site
    from_bank_sicredi.entrar_sicredi()

    # Download from bank every day
    for day_download in downloads_day:

        print(f'Downloading bank from date: {day_download}')

        day = datetime.strptime(day_download, '%d/%m/%Y')
        name = day.strftime('%Y-%m-%d')

        # Import to BD
        if import_bd is True:
            from_bank_sicredi.baixar_extrato(day)
        else:
            from_bank_sicredi.baixar_extrato(day)

    from_bank_sicredi.close_all()

