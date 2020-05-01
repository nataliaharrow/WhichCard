from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from .models import Card
from django.shortcuts import redirect
from cards.forms import CreditForm
from .object import ChosenCards
import operator
# Create your views here.


def home(request):
    return render(request, 'cards/homepage.html')


def get_display_cards(request):
    return render(request, 'cards/display_cards.html')


def get_info(request):
    # if this is a POST request we need to process the form data
    print("IN THE FORM")  # testing if we're in the method
    if request.method == 'POST':
        print("FORM IS VALID---")  # testing whether  form can be submitted
        # create a form instance and populate it with data from the request:
        form = CreditForm(request.POST)
        if form.is_valid():
            # extract the data from the form.cleaned_data
            groceries = form.cleaned_data['groceries']
            dining_out = form.cleaned_data['dining']
            gas = form.cleaned_data['gas']
            travel = form.cleaned_data['travels']
            everything_else = form.cleaned_data['etc']

            credit_score = form.cleaned_data['credit_score']
            annual = form.cleaned_data['annual']
            banks = form.cleaned_data['banks']
            if banks == ['all']:
                banks = ['Chase', 'Citibank', 'American Express', 'Capital One', 'Bank of America', 'Wells Fargo']
            # test, retrieving additional info
            print(credit_score)
            print(annual)
            print(banks)

            list_of_cards = get_best_cards(groceries, dining_out, gas, travel, everything_else)
            okay_cards=[]
            best_cards=[]

            for card in list_of_cards:
                card_obj = get_cards(card)
                okay_cards.append(card_obj)

            filtered_cards = filter_cards(banks, credit_score, annual, okay_cards);

            if len(filtered_cards) > 5:
                for i in range(5):
                    best_cards.append(filtered_cards[i])
            else:
                best_cards = filtered_cards

            context = {}
            context['best_cards'] = best_cards
            return render(request, 'cards/forms.html', context)
    # if a GET (or any other method) we'll create a blank form
    else:
        form = CreditForm()
    return render(request, 'cards/forms.html', {'form': form})


def get_cards(card_param):
    assert card_param is not None

    card = Card.objects.get(cardName=card_param)
    return card


def get_best_cards(grocery_input, dining_out_input, gas_input, travel_input, everything_else_input):
    # checking params are non negative values and are not empty

    assert grocery_input >= 0 and grocery_input is not None
    assert dining_out_input >= 0 and dining_out_input is not None
    assert gas_input >= 0 and gas_input is not None
    assert travel_input >= 0 and travel_input is not None
    assert everything_else_input >= 0 and everything_else_input is not None

    cards_by_value = ChosenCards()
    card_set = Card.objects.all()


    for card in card_set:
        card_value = float(calculate_card_value(card, grocery_input, dining_out_input, gas_input, travel_input,
                                          everything_else_input))
        if user_qualifies_for_bonus(card, grocery_input, dining_out_input, gas_input, travel_input, everything_else_input):
            card_value += card.bonusValue

        cards_by_value.chosen_cards[card.cardName] = card_value

    sorted_cards = sort_cards_by_value(cards_by_value.chosen_cards)
    list_of_cards = list(sorted_cards.keys())
    return list_of_cards

def user_qualifies_for_bonus(card, grocery_input, dining_out_input, gas_input, travel_input, everything_else_input):
    for parameter in list(locals().values())[1:]:
        assert parameter is not None

    user_spending = float((grocery_input + dining_out_input + gas_input + travel_input + everything_else_input)/12)

    # to avoid division by zero
    if card.bonusValue != 0 and card.bonusSpendMonths != 0:
        card_bonus_value_requirement = float(card.bonusMinimumSpend / card.bonusSpendMonths)
        if user_spending >= card_bonus_value_requirement:
            return True


def calculate_card_value(card, grocery_input, dining_out_input, gas_input, travel_input, everything_else_input):
    for parameter in list(locals().values())[1:]:
        assert parameter is not None

    card_grocer_multiplier = card.groceryMultiplier
    card_restaurant_multiplier = card.restMultiplier
    card_gas_multiplier = card.gasMultiplier
    card_travel_multiplier = card.travelMultiplier
    card_everything_else_multiplier = card.elseMultiplier
    card_reward_value = card.rewardValue
    card_annual_fee = card.annualFee

    card_value = float((((grocery_input * card_grocer_multiplier) + (dining_out_input * card_restaurant_multiplier)
                   + (gas_input * card_gas_multiplier) + (travel_input * card_travel_multiplier)
                   + (everything_else_input * card_everything_else_multiplier)) * card_reward_value) - card_annual_fee)

    return card_value

def filter_cards(banks_input, credit_score_input, annual_input, card_list):
    card_set = card_list
    f1 = []
    f2 = []
    f3 = []

    if annual_input == 'yes':
        for card in card_set:
            if card.annualFee == 0:
                f1.append(card)
    else: 
        for card in card_set:
            f1.append(card)

    if credit_score_input == 'bad':
        for i in f1:
            if i.creditScore == "Bad":
                f2.append(i)
    elif credit_score_input == 'average':
        for i in f1:
            if i.creditScore == "Bad" or i.creditScore == "Average":
                f2.append(i)
    elif credit_score_input == 'good':
        for i in f1:
            if i.creditScore == "Bad" or i.creditScore == "Average" or i.creditScore == "Good":
                f2.append(i)
    else: 
        for i in f1:
            f2.append(i)

    for k in f2:
        if k.bankName in banks_input:
            f3.append(k)

    return f3;


def sort_cards_by_value(cards):
    assert cards is not None

    return dict(sorted(cards.items(), key=operator.itemgetter(1), reverse=True))


def about_us(request):
    return render(request, 'cards/AboutUs.html')
