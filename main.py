# *-* coding: utf-8 *-*


def pick(operation_resource1, operation_resource2, resource_limit, resource):
    # Funkcja pick decyduje, która z operacji powinna zostać wykonana lub czy ewentualnie powinny zostać wykonane
    # obie równolegle.

    # Sprawdzamy czy zasoby w użyciu w sumie z zasobami potrzebnymi do operacji nie wykraczają za limit.
    # Funkcja zwaraca 4 wartości:
    # 1 - gdy powinna zostać wykonana operacja 1
    # 2 - gdy powinna zostać wykonana operacja 2
    # 3 - gdy powinny zostać wykonane obie równolegle
    # 0 - gdy niemożliwe jest wykonanie żadnej
    if resource + operation_resource1 + operation_resource2 <= resource_limit:
        return 3
    # Sprawdzamy czy możemy wykonać każdą operacje w tym samym czasie, ale nie równolegle.
    if resource + operation_resource1 <= resource_limit and resource + operation_resource2 <= resource_limit:
        # Tu sprawdzamy, która z operacji potrzebuje więcej zasobów.
        if operation_resource2 <= operation_resource1:
            return 1
        else:
            return 2
    if resource + operation_resource1 <= resource_limit:
        return 1
    if resource + operation_resource2 <= resource_limit:
        return 2
    return 0


def can_start(resource_limit, resource, operation, time, running_operations):
    # Funkcja ta sprawdza czy podana operacja może zostać wykonana.
    # Zwraca True, gdy może, a False w przeciwnym wypadku.

    # Jeżeli nie ma żadnych operacji, które się aktualnie wykonują, to oznacza, że możemy wykonać podaną operację
    if len(running_operations) == 0:
        return True

    # Ta zmienna będzie pamiętać, czy wykonuje się nadal jakaś operacja z tego samego zlecenia co podana operacja
    # True, gdy nie, a False w przeciwnym razie
    can_queue = True
    for running in running_operations:
        # Sprawdź czy operacje z tego samego zlecenia
        if running['id'] == operation['id']:
            can_queue = False
            # Sprawdź czy operacja, która nadal się wykonuje, nie powinna być zakończona
            if time == running['end']:
                return True

    return can_queue


def free_resource(time, resource, running_operations, ended_operations):
    # Funkcja wyzwala już nie używane zasoby (sprawdza, czy już jakieś operacje się zakończyły)
    # Ta lista przechowywuje operacje nadal aktywne, tuż po wyzwoleniu.
    operations = []

    if len(running_operations) == 0:
        return running_operations

    for running in running_operations:
        # Jeśli operacja jest zakończona, wyzwól zasoby oraz przenieś operację do listy operacji zakończonych.
        if time == running['end']:
            resource -= running['resource']
            ended_operations.append(running)
        else:
            # W przeciwnym razie ta operacja nadal jest aktywna.
            operations.append(running)

    return operations, resource


def readfile(filename):
    # Otwórz plik o nazwie filename i wczytaj wszystkie linie do listy o nazwie data.
    with open(filename) as file:
        data = file.readlines()

    # Musimy usunąć z lini znak końca lini, a następnie zamienić z ciągu znaków na liczbę.
    # maximum - limit zasobów
    maximum = float(data[0].lstrip('\n'))
    # Pierwszy wiersz jest już wczytane, tzn. możemy go wyrzucić.
    data.pop(0)

    # Zmienna, która mówi czy czytane operacje powinny należeć do drugiego zlecenia czy nie.
    second_set = False
    set1 = []
    set2 = []
    for line in data:
        # Gdy napotkamy słowo 'end', czytamy operacje do drugiego zlecenia.
        if line == 'end\n':
            second_set = True
            continue
        # Usuń znak końca linii, a następnie podziel na dwa elementy rozdzielone spacją.
        array = line.lstrip('\n').rsplit(sep = ' ')
        if not second_set:
            # Dodaj dane w postaci słownika:
            # id - zlecenie
            # duration - czas trwania
            # resource - potrzebny zasób
            set1.append({'id': 1, 'duration': float(array[1]), 'resource': float(array[0])})
        else:
            set2.append({'id': 2, 'duration': float(array[1]), 'resource': float(array[0])})

    return set1, set2, maximum


# Poproś użytkownika o nazwę pliku
path = input('Nazwa pliku: ')

# Odczytaj potrzebne informacje z pliku
first_assignment, second_assignment, limit = readfile(path)
# first_assignment - pierwsze zlecenie
# second_assignment - drugie zlecenie
# limit - limit zasobów
# running_operations - aktywne operacje
# ended_operations - zakończone operacje
# current_resource - zasoby aktualnie w użyciu
# current_time - obecny czas
# i - iterator pierwszego zlecenia
# j - iterator drugiego zlecenia
running_operations = []
ended_operations = []
current_resource = 0
current_time = 0
i = 0
j = 0


def start_operation(current_resource, iterator, operation):
    # Funkcja startuje operację tj. blokuje zasoby i wstawia do listy aktywnych operacji
    global current_time
    current_resource += operation['resource']
    running_operations.append({'resource': operation['resource'],
                               'end': operation['duration'] + current_time,
                               'duration': operation['duration'],
                               'id': operation['id']})

    # Teraz chcemy sprawdzić na jaki czas ustawić czas obecny
    # Jeżeli są aktywne dwie operacje - bierzemy wcześniejszy czas zakończenia
    if len(running_operations) == 2:
        current_time = min(running_operations[0]['end'], running_operations[1]['end'])
    else:
        # Gdy jedna to czas zakończenia tej operacji
        current_time = running_operations[0]['end']
    iterator += 1
    return current_resource, iterator


# Lecimy po wszystkich operacjach dopóki nie przelecimy obu zleceń
while True:
    # Gdy przelecieliśmy już przez obie listy, trzeba wyjść z pętli
    if (i >= len(first_assignment)) and (j >= len(second_assignment)):
        break
    # Gdy przelecieliśmy zlecenie pierwsze/zlecenie drugie, tworzymy operację, która nigdy nie zostania wykonana
    # w ten sposób możemy bezpiecznie przekazywać dalej dwie operacje do wszytkich funkcji.
    if i >= len(first_assignment):
        operation1 = {'id': 0, 'duration': 0, 'resource': limit + 1}
    else:
        # W przeciwnym razie weź operację ze zlecenia.
        operation1 = first_assignment[i]

    if j >= len(second_assignment):
        operation2 = {'id': 0, 'duration': 0, 'resource': limit + 1}
    else:
        operation2 = second_assignment[j]

    # Sprawdzamy co powinniśmy wybrać równolegle/pierwsze zlecenie/drugie zlecenie/nic
    selection = pick(operation1['resource'], operation2['resource'], limit, current_resource)
    # Równolegle
    if selection == 3:
        # Sprawdzamy czy możemy wykonać oba na raz
        if can_start(limit, current_resource, operation1, current_time, running_operations) and \
                can_start(limit, current_resource, operation2, current_time, running_operations):
            # Analogia jak w funkcji start_operations
            current_resource += operation1['resource'] + operation2['resource']
            running_operations.append({'resource': operation1['resource'],
                                       'end': operation1['duration'] + current_time,
                                       'duration': operation1['duration'],
                                       'id': operation1['id']})
            running_operations.append({'resource': operation2['resource'],
                                       'end': operation2['duration'] + current_time,
                                       'duration': operation2['duration'],
                                       'id': operation2['id']})
            current_time = min(running_operations[0]['end'], running_operations[1]['end'])
            i += 1
            j += 1
        else:
            # Jeżeli nie możemy to musimy wziąć późniejszy czas zakończenia aktywnych operacji
            for operation in running_operations:
                if current_time < operation['end']:
                    current_time = operation['end']
    elif selection == 1:
        # Pierwsze zlecenie
        # Sprawdzamy czy możemy wykonać pierwsze
        if can_start(limit, current_resource, operation1, current_time, running_operations):
            current_resource, i = start_operation(current_resource, i, operation1)
        elif can_start(limit, current_resource, operation2, current_time, running_operations):
            # Sprawdzamy czy w takim razie możemy wykonać drugie
            current_resource, j = start_operation(current_resource, j, operation2)
        else:
            # Jeżeli nie możemy to musimy wziąć późniejszy czas zakończenia aktywnych operacji
            for operation in running_operations:
                if current_time < operation['end']:
                    current_time = operation['end']
    elif selection == 2:
        # Pierwsze zlecenie
        # Sprawdzamy czy możemy wykonać drugie
        if can_start(limit, current_resource, operation2, current_time, running_operations):
            current_resource, j = start_operation(current_resource, j, operation2)
        elif can_start(limit, current_resource, operation1, current_time, running_operations):
            # Sprawdzamy czy możemy wykonać pierwsze
            current_resource, i = start_operation(current_resource, i, operation1)
        else:
            # Jeżeli nie możemy to musimy wziąć późniejszy czas zakończenia aktywnych operacji
            for operation in running_operations:
                if current_time < operation['end']:
                    current_time = operation['end']
    else:
        # Jeżeli pick sugeruje, że nie mógl niczego wybrać, musimy wziąć późniejszy czas zakończenia
        for operation in running_operations:
            if current_time < operation['end']:
                current_time = operation['end']

    # Uwalniamy i kończymy operacje aktywne (które oczywiście możemy zakończyć)
    running_operations, current_resource = free_resource(current_time, current_resource, running_operations,
                                                         ended_operations)

operation_id = 0
# Za każde z %d %f wstawiamy odpowiednią wartość po procencie poza cudzysłowiem
# %d - całkowita liczba
# %f - zmiennoprzecinkowa (wymierna) 
file = open('output.txt', w) 
for dictionary in ended_operations:
    file.write("%d: Start: %f, Koniec: %f, Zasoby: %f, Zlecenie: %d" %
        ..  (operation_id, dictionary['end'] - dictionary['duration'], dictionary['end'], dictionary['resource'],
           dictionary['id']))
