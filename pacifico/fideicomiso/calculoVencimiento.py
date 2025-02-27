import datetime

def add_one_month(dt):
    # Function to add one month to a date
    month = dt.month
    year = dt.year + month // 12
    month = month % 12 + 1
    day = min(dt.day, [31, 29 if year % 4 == 0 and not year % 100 == 0 or year % 400 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
    return dt.replace(year=year, month=month, day=day)

def calculate_fecha_vencimiento(plazo_pago, cot_fecha_inicio_pago, pagadiciembre1, forma_pago):
    aux_ai = plazo_pago
    wrk_fecha = cot_fecha_inicio_pago.date()

    wrk_dia3 = wrk_fecha.day
    wrk_num2_4 = wrk_dia3

    if forma_pago == 3:
        wrk_fecha -= datetime.timedelta(days=15)

    if forma_pago == 4 and wrk_dia3 <= 15:
        aux_a = 1
    else:
        aux_a = 0

    aux_b = 0

    while aux_a < aux_ai:
        wrk_mes = wrk_fecha.month
        wrk_dia = wrk_fecha.day
        wrk_num2_2 = wrk_mes
        wrk_num2_3 = wrk_dia

        if wrk_num2_2 == 1 and wrk_num2_3 == 30:
            wrk_fecha += datetime.timedelta(days=29)
        elif wrk_num2_2 == 2 and wrk_num2_3 == 28:
            wrk_fecha = wrk_fecha.replace(month=3, day=30)
        else:
            wrk_fecha = add_one_month(wrk_fecha)

        wrk_mes = wrk_fecha.month
        num2 = wrk_mes

        if num2 == 12:
            if pagadiciembre1 == "Y":
                aux_a += 1
        else:
            aux_a += 1

    fecha_vencimiento = wrk_fecha.strftime("%Y-%m-%d")
    print(fecha_vencimiento)
    print("-----------")
    
    return fecha_vencimiento
