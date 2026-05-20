from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from .models import Counterparty
from .forms import CounterpartyForm


def counterparty_list(request):
    query = request.GET.get('q', '')
    show_deleted = request.GET.get('show_deleted', '')

    counterparties = Counterparty.objects.all()

    if query:
        counterparties = counterparties.filter(
            Q(name__icontains=query) | Q(inn__icontains=query) | Q(code__icontains=query)
        )

    if not show_deleted:
        counterparties = counterparties.filter(is_marked_for_deletion=False)

    paginator = Paginator(counterparties, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'counterparties/counterparty_list.html', {
        'page_obj': page_obj,
        'query': query,
        'show_deleted': show_deleted,
    })


def counterparty_create(request):
    if request.method == 'POST':
        form = CounterpartyForm(request.POST)
        if form.is_valid():
            counterparty = form.save()
            messages.success(request, f'Контрагент "{counterparty.name}" создан!')
            result = counterparty.comprehensive_inn_check()
            if result['has_issues']:
                messages.warning(request, 'Внимание! Обнаружены возможные дубликаты по ИНН!')
            return redirect('counterparties:counterparty_detail', pk=counterparty.pk)
    else:
        form = CounterpartyForm()
    return render(request, 'counterparties/counterparty_form.html', {'form': form, 'title': 'Создание контрагента'})


def counterparty_detail(request, pk):
    counterparty = get_object_or_404(Counterparty, pk=pk)
    return render(request, 'counterparties/counterparty_detail.html', {'counterparty': counterparty})


def counterparty_edit(request, pk):
    counterparty = get_object_or_404(Counterparty, pk=pk)
    if request.method == 'POST':
        form = CounterpartyForm(request.POST, instance=counterparty)
        if form.is_valid():
            counterparty = form.save()
            messages.success(request, f'Контрагент "{counterparty.name}" обновлен!')
            return redirect('counterparties:counterparty_detail', pk=counterparty.pk)
    else:
        form = CounterpartyForm(instance=counterparty)
    return render(request, 'counterparties/counterparty_form.html',
                  {'form': form, 'title': 'Редактирование контрагента'})


def counterparty_delete(request, pk):
    counterparty = get_object_or_404(Counterparty, pk=pk)
    if request.method == 'POST':
        counterparty.is_marked_for_deletion = True
        counterparty.save()
        messages.success(request, f'Контрагент "{counterparty.name}" помечен на удаление')
        return redirect('counterparties:counterparty_list')
    return render(request, 'counterparties/counterparty_confirm_delete.html', {'counterparty': counterparty})


def check_inn_button(request, pk):
    counterparty = get_object_or_404(Counterparty, pk=pk)
    result = counterparty.comprehensive_inn_check()

    if result['exact_duplicates']:
        dup_list = ', '.join([f"{c.name} (код: {c.code})" for c in result['exact_duplicates']])
        messages.warning(request, f'⚠️ Найдены контрагенты с таким же ИНН: {dup_list}')
    if result['contains_other']:
        for c in result['contains_other']:
            messages.warning(request, f'📌 ИНН "{counterparty.inn}" входит в ИНН контрагента "{c.name}": {c.inn}')
    if result['part_of_other']:
        for c in result['part_of_other']:
            if c.inn != counterparty.inn:
                messages.warning(request, f'🔍 ИНН контрагента "{c.name}" ({c.inn}) входит в текущий ИНН')
    if not result['has_issues']:
        messages.success(request, '✅ Проверка пройдена! Совпадений не найдено.')

    return redirect('counterparties:counterparty_detail', pk=pk)


def find_all_duplicates(request):
    if request.method == 'POST':
        duplicate_inns = Counterparty.objects.filter(
            is_marked_for_deletion=False
        ).values('inn').annotate(count=Count('id')).filter(count__gt=1)

        found = []
        for item in duplicate_inns:
            duplicates = Counterparty.objects.filter(inn=item['inn'], is_marked_for_deletion=False)
            first = True
            for dup in duplicates:
                if not first:
                    dup.is_marked_for_deletion = True
                    dup.save()
                    found.append({'name': dup.name, 'code': dup.code, 'inn': dup.inn})
                first = False

        if found:
            messages.success(request, f'Найдено и помечено на удаление {len(found)} дубликатов')
            request.session['duplicate_list'] = found
        else:
            messages.info(request, 'Дубликатов не найдено')
        return redirect('counterparties:duplicate_check_result')

    return render(request, 'counterparties/duplicate_check_form.html')


def duplicate_check_result(request):
    duplicates = request.session.get('duplicate_list', [])
    return render(request, 'counterparties/duplicate_check_result.html', {'duplicates': duplicates})