import pandas as pd
from datetime import datetime, timedelta
import calendar
from events.persian_events import persian_events, persian_holidays, hijri_official_holidays
from events.gregorian_events import gregorian_events_en, gregorian_events_fa, gregorian_holidays
from events.hijri_events import hijri_events, hijri_events_en, hijri_holidays

start_year = int(input("Enter start year: "))
end_year = int(input("Enter end year: "))

def is_leap_year_persian(year):
    return (year % 33) in [1, 5, 9, 13, 17, 21, 25, 29]

def nth_weekday_of_month(year, month, weekday, n):
    """Find the nth occurrence of a weekday in a month"""
    first_day = datetime(year, month, 1)
    first_weekday = first_day.weekday()
    days_to_add = (weekday - first_weekday) % 7 + (n - 1) * 7
    target_date = first_day + timedelta(days=days_to_add)
    return target_date.day

def last_weekday_of_month(year, month, weekday):
    """Find the last occurrence of a weekday in a month"""
    last_day = calendar.monthrange(year, month)[1]
    last_date = datetime(year, month, last_day)
    last_weekday = last_date.weekday()
    days_to_subtract = (last_weekday - weekday) % 7
    target_date = last_date - timedelta(days=days_to_subtract)
    return target_date.day

def calculate_easter(year):
    """Calculate Easter date using the algorithm"""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return datetime(year, month, day)

def get_variable_holidays(year):
    """Get variable date holidays for a given year"""
    holidays = {}
    
    # Martin Luther King Jr. Day (3rd Monday of January)
    mlk_day = nth_weekday_of_month(year, 1, 0, 3)  # Monday = 0
    holidays[(1, mlk_day)] = 1
    
    # Washington's Birthday (3rd Monday of February)
    washington_day = nth_weekday_of_month(year, 2, 0, 3)
    holidays[(2, washington_day)] = 1
    
    # Memorial Day (Last Monday of May)
    memorial_day = last_weekday_of_month(year, 5, 0)
    holidays[(5, memorial_day)] = 1
    
    # Labor Day (1st Monday of September)
    labor_day = nth_weekday_of_month(year, 9, 0, 1)
    holidays[(9, labor_day)] = 1
    
    # Columbus Day (2nd Monday of October)
    columbus_day = nth_weekday_of_month(year, 10, 0, 2)
    holidays[(10, columbus_day)] = 1
    
    # Veterans Day (11th November) - Fixed date
    holidays[(11, 11)] = 1
    
    # Thanksgiving Day (4th Thursday of November)
    thanksgiving_day = nth_weekday_of_month(year, 11, 3, 4)  # Thursday = 3
    holidays[(11, thanksgiving_day)] = 1
    
    # Easter calculations
    easter = calculate_easter(year)
    good_friday = easter - timedelta(days=2)
    easter_monday = easter + timedelta(days=1)
    
    holidays[(good_friday.month, good_friday.day)] = 1
    holidays[(easter_monday.month, easter_monday.day)] = 1
    
    # UK Bank Holidays
    # Early May Bank Holiday (1st Monday of May)
    early_may_day = nth_weekday_of_month(year, 5, 0, 1)
    holidays[(5, early_may_day)] = 1
    
    # Spring Bank Holiday (Last Monday of May)
    spring_bank_day = last_weekday_of_month(year, 5, 0)
    holidays[(5, spring_bank_day)] = 1
    
    # Summer Bank Holiday (Last Monday of August)
    summer_bank_day = last_weekday_of_month(year, 8, 0)
    holidays[(8, summer_bank_day)] = 1
    
    return holidays

def jalali_to_gregorian(jy, jm, jd):
    jy += 1595
    days = -355668 + (365*jy) + ((jy//33)*8) + (((jy%33)+3)//4) + (31*(jm-1) if jm < 7 else (186 + (jm-7)*30)) + jd
    gy = 400 * (days // 146097)
    days %= 146097
    leap = True
    if days > 36524:
        gy += 100*(days//36524)
        days %= 36524
        if days >= 365:
            days += 1
        else:
            leap = False
    gy += 4*(days//1461)
    days %= 1461
    if days > 365:
        gy += (days-1)//365
        days = (days-1)%365
        leap = False
    gd_m = [0,31,59,90,120,151,181,212,243,273,304,334]
    for i in range(1,13):
        v = gd_m[i-1] + (1 if i > 2 and leap else 0)
        if i == 12 or days < gd_m[i] + (1 if i+1 > 2 and leap else 0):
            return gy, i, days - v + 1

# میلادی به عدد جولیَن
def gregorian_to_jd(gy, gm, gd):
    a = (14 - gm) // 12
    y = gy + 4800 - a
    m = gm + 12 * a - 3
    jd = gd + ((153 * m + 2) // 5) + 365 * y + (y // 4) - (y // 100) + (y // 400) - 32045
    return jd

# عدد جولیَن به قمری (الگوریتم حسابی دقیق)
def jd_to_hijri_tabular(jd):
    jd = int(jd)
    l = jd - 1948440 + 10632
    n = (l - 1) // 10631
    l = l - 10631 * n + 354
    j = ((10985 - l) // 5316) * ((50 * l) // 17719) + (l // 5670) * ((43 * l) // 15238)
    l = l - ((30 - j) // 15) * ((17719 * j) // 50) - (j // 16) * ((15238 * j) // 43) + 29
    m = (24 * l) // 709
    d = l - (709 * m) // 24
    y = 30 * n + j - 30
    return y, m, d

# ترکیب نهایی: میلادی → قمری
def gregorian_to_hijri(gy, gm, gd):
    jd = gregorian_to_jd(gy, gm, gd)
    return jd_to_hijri_tabular(jd)

def is_hijri_leap(year):
    """Check if Hijri year is leap year"""
    return ((11 * year + 14) % 30) < 11

def hijri_year_days(year):
    """Get number of days in Hijri year: 355 for leap, 354 for normal"""
    return 355 if is_hijri_leap(year) else 354

def day_of_week(gy, gm, gd):
    if gm < 3:
        gm += 12
        gy -= 1
    K, J = gy % 100, gy // 100
    h = (gd + (13*(gm + 1))//5 + K + (K//4) + (J//4) + (5*J)) % 7
    return (["شنبه","یکشنبه","دوشنبه","سه‌شنبه","چهارشنبه","پنج‌شنبه","جمعه"][h],
            ["Saturday","Sunday","Monday","Tuesday","Wednesday","Thursday","Friday"][h], h + 1)

persian_months = {1:"فروردین",2:"اردیبهشت",3:"خرداد",4:"تیر",5:"مرداد",6:"شهریور",7:"مهر",8:"آبان",9:"آذر",10:"دی",11:"بهمن",12:"اسفند"}
gregorian_months = {1:"January",2:"February",3:"March",4:"April",5:"May",6:"June",7:"July",8:"August",9:"September",10:"October",11:"November",12:"December"}
hijri_months = {1:"محرم",2:"صفر",3:"ربیع الاول",4:"ربیع الثانی",5:"جمادی الاول",6:"جمادی الثانی",7:"رجب",8:"شعبان",9:"رمضان",10:"شوال",11:"ذی القعده",12:"ذی حجه"}
seasons = {1:"بهار",2:"بهار",3:"بهار",4:"تابستان",5:"تابستان",6:"تابستان",7:"پاییز",8:"پاییز",9:"پاییز",10:"زمستان",11:"زمستان",12:"زمستان"}
half_years = {1:"نیمسال اول",2:"نیمسال اول",3:"نیمسال اول",4:"نیمسال اول",5:"نیمسال اول",6:"نیمسال اول",7:"نیمسال دوم",8:"نیمسال دوم",9:"نیمسال دوم",10:"نیمسال دوم",11:"نیمسال دوم",12:"نیمسال دوم"}


data = []
for year in range(start_year, end_year + 1):
    # Get variable holidays for this year
    variable_holidays = get_variable_holidays(year)
    
    for month in range(1, 13):
        days_in_month = 31 if month <= 6 else (30 if month <= 11 else (30 if is_leap_year_persian(year) else 29))
        for day in range(1, days_in_month + 1):
            gy, gm, gd = jalali_to_gregorian(year, month, day)
            persian_day, english_day, day_id = day_of_week(gy, gm, gd)
            greg_date = datetime(gy, gm, gd)
            get_season = lambda m: "Winter" if m in [12,1,2] else ("Spring" if m in [3,4,5] else ("Summer" if m in [6,7,8] else "Autumn"))
            
            # Check if this date is a variable holiday
            is_variable_holiday = variable_holidays.get((gm, gd), 0)
            gregorian_holiday_status = gregorian_holidays.get((gm, gd), 0) or is_variable_holiday
            
            # Check Persian holiday status (including Fridays as holidays)
            persian_holiday_status = persian_holidays.get((month, day), 0)
            if day_id == 7:  # Friday (جمعه) - always holiday
                persian_holiday_status = 1
            
            # Convert to Hijri date using accurate formula (Gregorian to Hijri)
            hy, hm, hd = gregorian_to_hijri(gy, gm, gd)
            
            # Check Hijri holiday status (including official Iranian Hijri holidays)
            hijri_holiday_status = hijri_holidays.get((hm, hd), 0)
            hijri_official_status = hijri_official_holidays.get((hm, hd), 0)
            hijri_holiday_status = hijri_holiday_status or hijri_official_status
            
            data.append({
                'shamsi_date': int(f"{year:04d}{month:02d}{day:02d}"),
                'miladi_date': f"{gy:04d}-{gm:02d}-{gd:02d}",
                'miladi_day_of_week_title': english_day,
                'shamsi_date_title': f"{year:04d}/{month:02d}/{day:02d}",
                'shamsi_next_date': int(f"{year:04d}{month:02d}{day+1:02d}") if day < days_in_month else (int(f"{year:04d}{month+1:02d}01") if month < 12 else int(f"{year+1:04d}0101")),
                'shamsi_month_id': int(f"{year:04d}{month:02d}"),
                'shamsi_month_title': f"{persian_months[month]} {year}",
                'shamsi_month_of_year_title': persian_months[month],
                'shamsi_season_id': int(f"{year:04d}{month:02d}"),
                'shamsi_season_title': f"{seasons[month]} {year}",
                'shamsi_half_year_id': int(f"{year:04d}{month:02d}"),
                'shamsi_half_year_title': f"{half_years[month]} {year}",
                'shamsi_year_id': year,
                'shamsi_month_of_year_id': month,
                'shamsi_day_of_month_id': day,
                'shamsi_day_of_year_id': sum([31 if m<=6 else (30 if m<=11 else (30 if is_leap_year_persian(year) else 29)) for m in range(1,month)]) + day,
                'shamsi_day_of_week_title': persian_day,
                'shamsi_day_of_week_id': day_id,
                'shamsi_event_name': persian_events.get((month, day)),
                'shamsi_is_holiday': persian_holiday_status,
                'shamsi_is_happy_holiday': persian_holiday_status,
                'shamsi_is_sad_holiday': 0,
                'shamsi_is_weekend': 1 if day_id in [6, 7] else 0,  # Thursday and Friday are weekends
                'gregorian_next_date': (greg_date + timedelta(days=1)).strftime('%Y-%m-%d'),
                'gregorian_month_id': int(f"{gy:04d}{gm:02d}"),
                'gregorian_month_title': f"{gregorian_months[gm]} {gy}",
                'gregorian_month_of_year_title': gregorian_months[gm],
                'gregorian_season_id': int(f"{gy:04d}{gm:02d}"),
                'gregorian_season_title': f"{get_season(gm)} {gy}",
                'gregorian_half_year_id': int(f"{gy:04d}{gm:02d}"),
                'gregorian_half_year_title': f"{'H1' if gm <= 6 else 'H2'} {gy}",
                'gregorian_year_id': gy,
                'gregorian_month_of_year_id': gm,
                'gregorian_day_of_month_id': gd,
                'gregorian_day_of_year_id': greg_date.timetuple().tm_yday,
                'gregorian_day_of_week_title': english_day,
                'gregorian_day_of_week_id': (greg_date.weekday() + 2) % 7 + 1,
                'gregorian_event_name_en': gregorian_events_en.get((gm, gd)),
                'gregorian_event_name_fa': gregorian_events_fa.get((gm, gd)),
                'gregorian_is_holiday': gregorian_holiday_status,
                'gregorian_is_happy_holiday': gregorian_holiday_status,
                'gregorian_is_sad_holiday': 0,
                'gregorian_is_weekend': 1 if greg_date.weekday() in [5, 6] else 0,
                'hijri_date': int(f"{hy:04d}{hm:02d}{hd:02d}"),
                'hijri_date_title': f"{hy:04d}/{hm:02d}/{hd:02d}",
                'hijri_month_id': int(f"{hy:04d}{hm:02d}"),
                'hijri_month_title': f"{hijri_months[hm]} {hy}",
                'hijri_month_of_year_title': hijri_months[hm],
                'hijri_year_id': hy,
                'hijri_month_of_year_id': hm,
                'hijri_day_of_month_id': hd,
                'hijri_event_name': hijri_events.get((hm, hd)),
                'hijri_event_name_en': hijri_events_en.get((hm, hd)),
                'hijri_is_holiday': hijri_holiday_status,
                'hijri_is_happy_holiday': hijri_holiday_status,
                'hijri_is_sad_holiday': 0,
            })

df = pd.DataFrame(data)

def assign_monthly_weeks(df_month):
    df_month = df_month.sort_values('shamsi_date').copy()
    is_saturday = (df_month['shamsi_day_of_week_id'] == 1)
    week_break = is_saturday.astype(int)
    if len(week_break) > 0:
        week_break.iloc[0] = 0
    df_month['week_num_in_month'] = 1 + week_break.cumsum()
    df_month['shamsi_week_id'] = df_month['shamsi_month_id'].astype(str) + '_' + df_month['week_num_in_month'].astype(int).astype(str)
    return df_month

def assign_yearly_weeks(df_year):
    df_year = df_year.sort_values(['shamsi_month_id','shamsi_date']).copy()
    is_saturday = (df_year['shamsi_day_of_week_id'] == 1)
    week_break = is_saturday.astype(int)
    if len(week_break) > 0:
        week_break.iloc[0] = 0
    df_year['week_num_in_year'] = 1 + week_break.cumsum()
    return df_year

df = df.sort_values(['shamsi_month_id','shamsi_date']).groupby('shamsi_month_id', group_keys=False).apply(assign_monthly_weeks)
df = df.groupby('shamsi_year_id', group_keys=False).apply(assign_yearly_weeks)
df['shamsi_week_title'] = df.apply(lambda row: f"هفته {int(row['week_num_in_year'])} سال {int(row['shamsi_year_id'])}", axis=1)
df['shamsi_week_of_year_id'] = df.apply(lambda row: f"{int(row['shamsi_year_id']):04d}_{int(row['week_num_in_year']):02d}", axis=1)

dates = pd.to_datetime(df['miladi_date'])
iso = dates.dt.isocalendar()
df['gregorian_week_id'] = iso['week'].astype(int)
df['gregorian_week_title'] = df.apply(lambda row: f"Week {row['gregorian_week_id']} {row['gregorian_year_id']}", axis=1)
df['gregorian_week_of_year_id'] = df.apply(lambda row: f"{int(row['gregorian_year_id']):04d}_{int(row['gregorian_week_id']):02d}", axis=1)
df['miladi_week_id'] = iso['week'].astype(int)
df['miladi_week_num_in_month'] = df.groupby(dates.dt.to_period('M').astype(str))['miladi_week_id'].transform(lambda s: s.rank(method='dense').astype(int))

final_columns = ['shamsi_date','miladi_date','miladi_day_of_week_title','shamsi_date_title','shamsi_next_date','shamsi_month_id','shamsi_month_title','shamsi_month_of_year_title','shamsi_season_id','shamsi_season_title','shamsi_half_year_id','shamsi_half_year_title','shamsi_year_id','shamsi_month_of_year_id','shamsi_day_of_month_id','shamsi_day_of_year_id','shamsi_day_of_week_title','shamsi_week_id','shamsi_week_title','shamsi_week_of_year_id','shamsi_day_of_week_id','shamsi_event_name','shamsi_is_holiday','shamsi_is_happy_holiday','shamsi_is_sad_holiday','shamsi_is_weekend','gregorian_next_date','gregorian_month_id','gregorian_month_title','gregorian_month_of_year_title','gregorian_season_id','gregorian_season_title','gregorian_half_year_id','gregorian_half_year_title','gregorian_year_id','gregorian_month_of_year_id','gregorian_day_of_month_id','gregorian_day_of_year_id','gregorian_day_of_week_title','gregorian_week_id','gregorian_week_title','gregorian_week_of_year_id','gregorian_day_of_week_id','gregorian_event_name_en','gregorian_event_name_fa','gregorian_is_holiday','gregorian_is_happy_holiday','gregorian_is_sad_holiday','gregorian_is_weekend','hijri_date','hijri_date_title','hijri_month_id','hijri_month_title','hijri_month_of_year_title','hijri_year_id','hijri_month_of_year_id','hijri_day_of_month_id','hijri_event_name','hijri_event_name_en','hijri_is_holiday','hijri_is_happy_holiday','hijri_is_sad_holiday','miladi_week_id','miladi_week_num_in_month']
df_final = df[final_columns].copy()

print(f"\nTotal days: {len(df_final):,}, Columns: {len(df_final.columns)}")
print(df_final.head())

filename = f"date_dimension_{df_final['shamsi_year_id'].min()}_{df_final['shamsi_year_id'].max()}.xlsx"
with pd.ExcelWriter(filename, engine='openpyxl') as writer:
    df_final.to_excel(writer, sheet_name='Date_Dimension', index=False)
    worksheet = writer.sheets['Date_Dimension']
    for column in worksheet.columns:
        max_length = max([len(str(cell.value)) for cell in column if cell.value] + [0])
        worksheet.column_dimensions[column[0].column_letter].width = min(max_length + 2, 50)

print(f"✅ Saved: {filename}")

