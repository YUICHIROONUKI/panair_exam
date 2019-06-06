from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import Customer, Record, Subject
from .forms import CustomerForm, RecordForm, MonthForm
import datetime

# メニュー一覧画面↓
def index(request):
    return render(request, 'school/index.html')

# 顧客一覧表示↓
def customers(request):
    customer_list = Customer.objects.all()
    header = ['ID', '名前', '性別', '年齢', '']
    context = {'customer_list': customer_list, 'header': header}
    return render(request, 'school/customers.html', context)

# 顧客新規登録画面↓
def new_user(request):
    form = CustomerForm()
    return render(request, 'school/new_user.html', {'form': form})

# 顧客新規登録DB保存↓
def create_user(request):
    form = CustomerForm(request.POST)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('school:customers'))

# 顧客情報編集画面・DB保存↓
def edit_user(request, id):
    obj = Customer.objects.get(id=id)
    if (request.method == 'POST'):
        customer = CustomerForm(request.POST, instance=obj)
        customer.save()
        return HttpResponseRedirect(reverse('school:customers'))
    edit_info = {
        'form': CustomerForm(instance=obj),
        'id': id
    }
    return render(request, 'school/edit_user.html', edit_info)

# レッスン受講履歴一覧↓
def lesson_records(request):
    form = MonthForm()
    customers = Customer.objects.all().prefetch_related("record_set")
    # 選択された月の取得↓
    if request.method == 'POST':
        form = MonthForm(request.POST)
        receive = request.POST['請求月']
    else:
        receive = str(datetime.date.today())[:-3]
    customers = Customer.objects.all()
    record_list = Record.objects.all().select_related().filter(study_date__startswith=receive).order_by('study_date')
    # 顧客毎の受講時間を保存する辞書を定義↓
    customer_finance_study_hour = {}
    customer_programing_study_hour = {}
    for customer in customers:
        customer_finance_study_hour[customer.customer_name] = 0
        customer_programing_study_hour[customer.customer_name] = 0
    # 受講日順に取得した学習履歴のレコードを展開し顧客の支払額を算出↓
    for record in record_list:
        record.customer_name = record.customer.customer_name
        record.subject_name = record.subject.subject_name
        # 受講したレッスンが英語の場合↓
        if record.subject_name == '英語':
            record.pay_money = record.study_hour * 3500
        # 受講したレッスンがファイナンスの場合↓
        elif record.subject_name == 'ファイナンス':
            customer_finance_study_hour[record.customer_name] += record.study_hour
            finance_study_hour = customer_finance_study_hour[record.customer_name]
            if finance_study_hour <= 20:
                record.pay_money = record.study_hour * 3300
            elif finance_study_hour <= 50:
                if finance_study_hour - record.study_hour <= 20:
                    record.pay_money = (20 - (finance_study_hour - record.study_hour)) * 3300 + (finance_study_hour - 20) * 2800
                else:
                    record.pay_money = record.study_hour * 2800
            elif finance_study_hour - record.study_hour <= 50:
                record.pay_money = (50 - (finance_study_hour - record.study_hour)) * 2800 + (finance_study_hour - 50) * 2500
            else:
                record.pay_money = record.study_hour * 2500
        # 受講したレッスンがプログラミングの場合↓
        else:
            customer_programing_study_hour[record.customer_name] += record.study_hour
            programing_study_hour = customer_programing_study_hour[record.customer_name]
            if programing_study_hour <= 5:
                record.pay_money = record.study_hour * 0
            elif programing_study_hour <= 20:
                if programing_study_hour - record.study_hour <= 5:
                    record.pay_money = (5 - (programing_study_hour - record.study_hour)) * 0 + (programing_study_hour - 5) * 3500
                else:
                    record.pay_money = record.study_hour * 3500
            elif programing_study_hour <= 35:
                if programing_study_hour - record.study_hour <= 20:
                    record.pay_money = (20 - (programing_study_hour - record.study_hour)) * 3500 + (programing_study_hour - 20) * 3000
                else:
                    record.pay_money = record.study_hour * 3000
            elif programing_study_hour <= 50:
                if programing_study_hour - record.study_hour <= 35:
                    record.pay_money = (35 - (programing_study_hour - record.study_hour)) * 3000 + (programing_study_hour - 20) * 2800
                else:
                    record.pay_money = record.study_hour * 2800
            elif programing_study_hour - record.study_hour <= 50:
                record.pay_money = (50 - (programing_study_hour - record.study_hour)) * 2800 + (programing_study_hour - 20) * 2500
            else:
                record.pay_money = record.study_hour * 2500
    header = ['ID', '受講者', 'ジャンル', '受講日', '受講時間', '支払い金額', '']
    context = {
        'record_list': record_list,
        'header': header,
        'form': form,
    }
    return render(request, 'school/lesson_records.html', context)

# レッスン受講記録登録画面・DB保存↓
def new_record(request):
    customers = Customer.objects.all()
    genre = Subject.objects.all()
    # DB保存↓
    if (request.method == 'POST'):
        obj = Record()
        record = RecordForm(request.POST, instance=obj)
        if record.is_valid():
            post = record.save(commit=False)
            post.customer_id = int(request.POST['customer_id'])
            post.subject_id = int(request.POST['subject_id'])
            post.save()
            return HttpResponseRedirect(reverse('school:lesson_records'))
        else:
            errors = "受講時間は1-12で入力してください"
            record_form = {
                'form':RecordForm(instance=obj),
                'customers':customers,
                'genre':genre,
                'errors': errors
            }
            return render(request, 'school/new_record.html', record_form)
    # 登録画面↓
    record_form = {
        'form':RecordForm(),
        'customers':customers,
        'genre':genre
    }
    return render(request, 'school/new_record.html', record_form)

# レッスン受講記録編集画面・DB保存↓
def edit_record(request, id):
    obj = Record.objects.get(id=id)
    customers = Customer.objects.all()
    genre = Subject.objects.all()
    # DB保存↓
    if (request.method == 'POST'):
        record = RecordForm(request.POST, instance=obj)
        if record.is_valid():
            post = record.save(commit=False)
            post.customer_id = int(request.POST['customer_id'])
            post.subject_id = int(request.POST['subject_id'])
            post.save()
            return HttpResponseRedirect(reverse('school:lesson_records'))
        else:
            errors = "受講時間は1-12で入力してください"
            edit_info = {
                'form': RecordForm(instance=obj),
                'id': id,
                'customers':customers,
                'genre': genre,
                'errors': errors
            }
            return render(request, 'school/edit_record.html', edit_info)
    # 編集画面↓
    edit_info = {
        'form': RecordForm(instance=obj),
        'id': id,
        'customers':customers,
        'genre':genre
    }
    return render(request, 'school/edit_record.html', edit_info)

# 月別請求一覧画面↓
def billings(request):
    form = MonthForm()
    customers = Customer.objects.all().prefetch_related("record_set")
    # 選択された月の取得↓
    if request.method == 'POST':
        form = MonthForm(request.POST)
        receive = request.POST['請求月']
    else:
        receive = str(datetime.date.today())[:-3]
    # 顧客を展開↓
    for customer in customers:
        # 顧客毎のレッスン数を算出↓
        customer_english_records = customer.record_set.filter(subject_id=1, study_date__startswith=receive)
        customer_finance_records = customer.record_set.filter(subject_id=2, study_date__startswith=receive)
        customer_programing_records = customer.record_set.filter(subject_id=3, study_date__startswith=receive)
        customer.english_lesson_count = len(customer_english_records)
        customer.finance_lesson_count = len(customer_finance_records)
        customer.programing_lesson_count = len(customer_programing_records)
        customer.lesson_total = len(customer_english_records) + len(customer_finance_records) + len(customer_programing_records)
        # 受講したレッスンの内訳↓
        if customer.english_lesson_count != 0 and customer.finance_lesson_count != 0 and customer.programing_lesson_count != 0:
            customer.genre = '英語/ファイナンス/プログラミング(3)'
        elif customer.english_lesson_count != 0 and customer.finance_lesson_count != 0:
            customer.genre = '英語/ファイナンス(2)'
        elif customer.finance_lesson_count != 0 and customer.programing_lesson_count != 0:
            customer.genre = 'ファイナンス/プログラミング(2)'
        elif customer.english_lesson_count != 0 and customer.programing_lesson_count != 0:
            customer.genre = '英語/プログラミング(2)'
        elif customer.english_lesson_count != 0:
            customer.genre = '英語(1)'
        elif customer.finance_lesson_count != 0:
            customer.genre = 'ファイナンス(1)'
        elif customer.programing_lesson_count != 0:
            customer.genre = 'プログラミング(1)'
        else:
            customer.genre = 'なし'
        # 各レッスンにおける請求額の算出↓
        english_total = 0
        for english_record in customer_english_records:
            english_total += english_record.study_hour
        if english_total == 0:
            customer.english_bill = 0
        else:
            customer.english_bill = 5000 + english_total * 3500

        finance_total = 0
        for finance_record in customer_finance_records:
            finance_total += finance_record.study_hour
        if finance_total <= 20:
            customer.finance_bill = finance_total * 3300
        elif finance_total <= 50:
            customer.finance_bill = 20 * 3300 + (finance_total - 20) * 2800
        else:
            customer.finance_bill = 20 * 3300 + 30 * 2800 + (finance_total - 50) * 2500

        programing_total = 0
        for programing_record in customer_programing_records:
            programing_total += programing_record.study_hour
        if programing_total == 0:
            customer.programing_bill = 0
        elif programing_total <= 5:
            customer.programing_bill = 20000
        elif programing_total <= 20:
            customer.programing_bill = 20000 + (programing_total - 5) * 3500
        elif programing_total <= 35:
            customer.programing_bill = 20000 + 15 * 3500 + (programing_total - 20) * 3000
        elif programing_total <= 50:
            customer.programing_bill = 20000 + 15 * 3500 + 15 * 3000 + (programing_total - 35) * 2800
        else:
            customer.programing_bill = 20000 + 15 * 3500 + 15 * 3000 + 15 * 2800 + (programing_total - 50) * 2500
        
        customer.total_bill = customer.programing_bill + customer.finance_bill + customer.english_bill
    header = ['顧客ID', '顧客名', 'ジャンル', '合計レッスン数', '請求金額']
    context = {
        'header': header,
        'customers': customers,
        'form': form,
    }
    return render(request, 'school/billings.html', context)

# レポート一覧表示↓
def report(request):

    # 年代ごとのレッスン数、受講者数、売り上げのデフォルト値を保存するメソッド↓
    def count_default(age):
        english_man_lesson_count[age] = 0
        english_woman_lesson_count[age] = 0
        finance_man_lesson_count[age] = 0
        finance_woman_lesson_count[age] = 0
        programing_man_lesson_count[age] = 0
        programing_woman_lesson_count[age] = 0
        english_man_customer_count[age] = 0
        english_woman_customer_count[age] = 0
        finance_man_customer_count[age] = 0
        finance_woman_customer_count[age] = 0
        programing_man_customer_count[age] = 0
        programing_woman_customer_count[age] = 0
        english_man_total_bill[age] = 0
        english_woman_total_bill[age] = 0
        finance_man_total_bill[age] = 0
        finance_woman_total_bill[age] = 0
        programing_man_total_bill[age] = 0
        programing_woman_total_bill[age] = 0

    # 年代ごとのレッスン数、受講者数、売り上げを算出するメソッド↓
    def age_customers_report(age_customers):
        for customer in age_customers:
            # 女性と男性で条件分岐↓
            if customer.sex == '男':
                # 顧客の持つ受け取った月の受講記録を取得↓
                man_english_records = customer.record_set.filter(subject_id=1, study_date__startswith=receive)
                man_finance_records = customer.record_set.filter(subject_id=2, study_date__startswith=receive)
                man_programing_records = customer.record_set.filter(subject_id=3, study_date__startswith=receive)
                # 年代ごとの各レッスン数を算出↓
                english_man_lesson_count[age] += len(man_english_records)
                finance_man_lesson_count[age] += len(man_finance_records)
                programing_man_lesson_count[age] += len(man_programing_records)
                # 年代毎の受講者数を算出↓
                if len(man_english_records) != 0:
                    english_man_customer_count[age] += 1
                if len(man_finance_records) != 0:
                    finance_man_customer_count[age] += 1
                if len(man_programing_records) != 0:
                    programing_man_customer_count[age] += 1
                # 年代毎の各レッスンにおける売り上げを算出↓
                man_english_total_hour = 0
                for man_english_record in man_english_records:
                    man_english_total_hour += man_english_record.study_hour
                if man_english_total_hour == 0:
                    man_english_bill = 0
                else:
                    man_english_bill = 5000 + man_english_total_hour * 3500
                english_man_total_bill[age] += man_english_bill

                man_finance_total_hour = 0
                for man_finance_record in man_finance_records:
                    man_finance_total_hour += man_finance_record.study_hour
                if man_finance_total_hour <= 20:
                    man_finance_bill = man_finance_total_hour * 3300
                elif man_finance_total_hour <= 50:
                    man_finance_bill = 20 * 3300 + (man_finance_total_hour - 20) * 2800
                else:
                    man_finance_bill = 20 * 3300 + 30 * 2800 + (man_finance_total_hour - 50) * 2500
                finance_man_total_bill[age] += man_finance_bill

                man_programing_total_hour = 0
                for man_programing_record in man_programing_records:
                    man_programing_total_hour += man_programing_record.study_hour
                if man_programing_total_hour == 0:
                    man_programing_bill = 0
                elif man_programing_total_hour <= 5:
                    man_programing_bill = 20000
                elif man_programing_total_hour <= 20:
                    man_programing_bill = 20000 + (man_programing_total_hour - 5) * 3500
                elif man_programing_total_hour <= 35:
                    man_programing_bill = 20000 + 15 * 3500 + (man_programing_total_hour - 20) * 3000
                elif man_programing_total_hour <= 50:
                    man_programing_bill = 20000 + 15 * 3500 + 15 * 3000 + (man_programing_total_hour - 35) * 2800
                else:
                    man_programing_bill = 20000 + 15 * 3500 + 15 * 3000 + 15 * 2800 + (man_programing_total_hour - 50) * 2500
                programing_man_total_bill[age] += man_programing_bill
            # 女性↓
            else:
                woman_english_records = customer.record_set.filter(subject_id=1, study_date__startswith=receive)
                woman_finance_records = customer.record_set.filter(subject_id=2, study_date__startswith=receive)
                woman_programing_records = customer.record_set.filter(subject_id=3, study_date__startswith=receive)
                english_woman_lesson_count[age] += len(woman_english_records)
                finance_woman_lesson_count[age] += len(woman_finance_records)
                programing_woman_lesson_count[age] += len(woman_programing_records)
                if len(woman_english_records) != 0:
                    english_woman_customer_count[age] += 1
                if len(woman_finance_records) != 0:
                    finance_woman_customer_count[age] += 1
                if len(woman_programing_records) != 0:
                    programing_woman_customer_count[age] += 1
                woman_english_total_hour = 0
                for woman_english_record in woman_english_records:
                    woman_english_total_hour += woman_english_record.study_hour
                if woman_english_total_hour == 0:
                    woman_english_bill = 0
                else:
                    woman_english_bill = 5000 + woman_english_total_hour * 3500
                english_woman_total_bill[age] += woman_english_bill

                woman_finance_total_hour = 0
                for woman_finance_record in woman_finance_records:
                    woman_finance_total_hour += woman_finance_record.study_hour
                if woman_finance_total_hour <= 20:
                    woman_finance_bill = woman_finance_total_hour * 3300
                elif woman_finance_total_hour <= 50:
                    woman_finance_bill = 20 * 3300 + (woman_finance_total_hour - 20) * 2800
                else:
                    woman_finance_bill = 20 * 3300 + 30 * 2800 + (woman_finance_total_hour - 50) * 2500
                finance_woman_total_bill[age] += woman_finance_bill

                woman_programing_total_hour = 0
                for woman_programing_record in woman_programing_records:
                    woman_programing_total_hour += woman_programing_record.study_hour
                if woman_programing_total_hour == 0:
                    woman_programing_bill = 0
                elif woman_programing_total_hour <= 5:
                    woman_programing_bill = 20000
                elif woman_programing_total_hour <= 20:
                    woman_programing_bill = 20000 + (woman_programing_total_hour - 5) * 3500
                elif woman_programing_total_hour <= 35:
                    woman_programing_bill = 20000 + 15 * 3500 + (woman_programing_total_hour - 20) * 3000
                elif woman_programing_total_hour <= 50:
                    woman_programing_bill = 20000 + 15 * 3500 + 15 * 3000 + (woman_programing_total_hour - 35) * 2800
                else:
                    woman_programing_bill = 20000 + 15 * 3500 + 15 * 3000 + 15 * 2800 + (woman_programing_total_hour - 50) * 2500
                programing_woman_total_bill[age] += woman_programing_bill


    form = MonthForm()
    customers = Customer.objects.all().prefetch_related("record_set")
    # 選択された月の取得↓
    if request.method == 'POST':
        form = MonthForm(request.POST)
        receive = request.POST['請求月']
    else:
        receive = str(datetime.date.today())[:-3]
    customers = Customer.objects.all().prefetch_related("record_set")
    customers_men = Customer.objects.filter(sex='男').prefetch_related("record_set")
    customers_women = Customer.objects.filter(sex='女').prefetch_related("record_set")
    # レッスン数のリスト、受講者数のリスト、売り上げのリストを定義↓
    english_man_lesson_count = {}
    english_woman_lesson_count = {}
    finance_man_lesson_count = {}
    finance_woman_lesson_count = {}
    programing_man_lesson_count = {}
    programing_woman_lesson_count = {}
    english_man_customer_count = {}
    english_woman_customer_count = {}
    finance_man_customer_count = {}
    finance_woman_customer_count = {}
    programing_man_customer_count = {}
    programing_woman_customer_count = {}
    english_man_total_bill = {}
    english_woman_total_bill = {}
    finance_man_total_bill = {}
    finance_woman_total_bill = {}
    programing_man_total_bill = {}
    programing_woman_total_bill = {}
    # 全ての年代のレッスン数、受講者数、売り上げの合計を格納する変数を定義↓
    english_man_lesson_count_total = 0
    english_woman_lesson_count_total = 0
    finance_man_lesson_count_total = 0
    finance_woman_lesson_count_total = 0
    programing_man_lesson_count_total = 0
    programing_woman_lesson_count_total = 0
    english_man_customer_count_total = 0
    english_woman_customer_count_total = 0
    finance_man_customer_count_total = 0
    finance_woman_customer_count_total = 0
    programing_man_customer_count_total = 0
    programing_woman_customer_count_total = 0
    english_man_total_bill_total = 0
    english_woman_total_bill_total = 0
    finance_man_total_bill_total = 0
    finance_woman_total_bill_total = 0
    programing_man_total_bill_total = 0
    programing_woman_total_bill_total = 0

    # 年代を識別するためのリストを定義(10代は1,20代は2)↓
    ages = ['1', '2', '3', '4', '5', '6', '7', '8']

    # 10〜80代のレポートを算出↓
    for age in ages:
        count_default(age)
    for age in ages:
        from_10_to_89_old_customers = list(filter(lambda x: x.age >= 10 and x.age <= 89, customers))
        ages_customers = list(filter(lambda x: str(x.age)[-2] == age, from_10_to_89_old_customers))
        age_customers_report(ages_customers)
    for age in ages:
        english_man_lesson_count_total += english_man_lesson_count[age]
        english_woman_lesson_count_total += english_woman_lesson_count[age]
        finance_man_lesson_count_total += finance_man_lesson_count[age]
        finance_woman_lesson_count_total += finance_woman_lesson_count[age]
        programing_man_lesson_count_total += programing_man_lesson_count[age]
        programing_woman_lesson_count_total += programing_woman_lesson_count[age]
        english_man_customer_count_total += english_man_customer_count[age]
        english_woman_customer_count_total += english_woman_customer_count[age]
        finance_man_customer_count_total += finance_man_customer_count[age]
        finance_woman_customer_count_total += finance_woman_customer_count[age]
        programing_man_customer_count_total += programing_man_customer_count[age]
        programing_woman_customer_count_total += programing_woman_customer_count[age]
        english_man_total_bill_total += english_man_total_bill[age]
        english_woman_total_bill_total += english_woman_total_bill[age]
        finance_man_total_bill_total += finance_man_total_bill[age]
        finance_woman_total_bill_total += finance_woman_total_bill[age]
        programing_man_total_bill_total += programing_man_total_bill[age]
        programing_woman_total_bill_total += programing_woman_total_bill[age]

    # 10〜80代以外のレポートを算出↓
    customers = Customer.objects.all().prefetch_related("record_set")
    age = "under_9_or_over_90_old"
    count_default(age)
    under_9_or_over_90_old_customers = list(filter(lambda x: x.age <= 9 or x.age >= 90, customers))
    age_customers_report(under_9_or_over_90_old_customers)
    # 全ての顧客の性別別のレポートを算出↓
    english_man_lesson_count_total += english_man_lesson_count[age]
    english_woman_lesson_count_total += english_woman_lesson_count[age]
    finance_man_lesson_count_total += finance_man_lesson_count[age]
    finance_woman_lesson_count_total += finance_woman_lesson_count[age]
    programing_man_lesson_count_total += programing_man_lesson_count[age]
    programing_woman_lesson_count_total += programing_woman_lesson_count[age]
    english_man_customer_count_total += english_man_customer_count[age]
    english_woman_customer_count_total += english_woman_customer_count[age]
    finance_man_customer_count_total += finance_man_customer_count[age]
    finance_woman_customer_count_total += finance_woman_customer_count[age]
    programing_man_customer_count_total += programing_man_customer_count[age]
    programing_woman_customer_count_total += programing_woman_customer_count[age]
    english_man_total_bill_total += english_man_total_bill[age]
    english_woman_total_bill_total += english_woman_total_bill[age]
    finance_man_total_bill_total += finance_man_total_bill[age]
    finance_woman_total_bill_total += finance_woman_total_bill[age]
    programing_man_total_bill_total += programing_man_total_bill[age]
    programing_woman_total_bill_total += programing_woman_total_bill[age]

    # ジャンルと性別別に分けた辞書をリストに格納↓
    genre_sex_list =[]
    genre_sex_list.append({'genre': '英語', 'sex': '男', 'lesson_count': english_man_lesson_count_total, 'customer_count': english_man_customer_count_total, 'total_bill': english_man_total_bill_total})
    genre_sex_list.append({'genre': '英語', 'sex': '女', 'lesson_count': english_woman_lesson_count_total, 'customer_count': english_woman_customer_count_total, 'total_bill': english_woman_total_bill_total})
    genre_sex_list.append({'genre': 'ファイナンス', 'sex': '男', 'lesson_count': finance_man_lesson_count_total, 'customer_count': finance_man_customer_count_total, 'total_bill': finance_man_total_bill_total})
    genre_sex_list.append({'genre': 'ファイナンス', 'sex': '女', 'lesson_count': finance_woman_lesson_count_total, 'customer_count': finance_woman_customer_count_total, 'total_bill': finance_woman_total_bill_total})
    genre_sex_list.append({'genre': 'プログラミング', 'sex': '男', 'lesson_count': programing_man_lesson_count_total, 'customer_count': programing_man_customer_count_total, 'total_bill': programing_man_total_bill_total})
    genre_sex_list.append({'genre': 'プログラミング', 'sex': '女', 'lesson_count': programing_woman_lesson_count_total, 'customer_count': programing_woman_customer_count_total, 'total_bill': programing_woman_total_bill_total})
    # ジャンルと年代別に分けた辞書をリストに格納↓
    genre_age_list = []
    for age in ages:
        genre_age_list.append({'genre': '英語', 'sex': '男', 'age': age + '0代', 'lesson_count': english_man_lesson_count[age], 'customer_count': english_man_customer_count[age], 'total_bill': english_man_total_bill[age]})
    for age in ages:
        genre_age_list.append({'genre': '英語', 'sex': '女', 'age': age + '0代', 'lesson_count': english_woman_lesson_count[age], 'customer_count': english_woman_customer_count[age], 'total_bill': english_woman_total_bill[age]})
    for age in ages:
        genre_age_list.append({'genre': 'ファイナンス', 'sex': '男', 'age': age + '0代', 'lesson_count': finance_man_lesson_count[age], 'customer_count': finance_man_customer_count[age], 'total_bill': finance_man_total_bill[age]})
    for age in ages:
        genre_age_list.append({'genre': 'ファイナンス', 'sex': '女', 'age': age + '0代', 'lesson_count': finance_woman_lesson_count[age], 'customer_count': finance_woman_customer_count[age], 'total_bill': finance_woman_total_bill[age]})
    for age in ages:
        genre_age_list.append({'genre': 'プログラミング', 'sex': '男', 'age': age + '0代', 'lesson_count': programing_man_lesson_count[age], 'customer_count': programing_man_customer_count[age], 'total_bill': programing_man_total_bill[age]})
    for age in ages:
        genre_age_list.append({'genre': 'プログラミング', 'sex': '女', 'age': age + '0代', 'lesson_count': programing_woman_lesson_count[age], 'customer_count': programing_woman_customer_count[age], 'total_bill': programing_woman_total_bill[age]})
    genre_sex = ['ジャンル', '性別', 'レッスン数', '受講者数', '売り上げ']
    genre_age = ['ジャンル', '性別', '年齢像別', 'レッスン数', '受講者数', '売り上げ']
    context = {
        'genre_sex': genre_sex,
        'genre_age': genre_age,
        'genre_sex_list': genre_sex_list,
        'genre_age_list': genre_age_list,
        'form': form,
    }
    return render(request, 'school/report.html', context)
