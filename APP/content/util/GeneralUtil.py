import io
import re
import random
import string
import collections
from django.conf import settings
from collections import defaultdict, OrderedDict
from itertools import chain
import markdown
import ruamel.yaml
from content.models import Question

from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth

from content.models import CourseSubscription
from djstripe.models import (
        Subscription,
        Discount,
    )
current_month = datetime.now().date()
n_months = 6

def TagGenerator():
    x = ''.join(
            random.choices(string.ascii_letters + string.digits, k=10)
        ).lower()
    return x

def ChapterQuestionGenerator(user, subject, module, module_content):
    difficulty_levels = [1, 2, 3, 4, 5]
    for chapter in module_content.keys():
        chapter_qs = module_content[chapter]['questions']
        for diff_level in difficulty_levels:
            if str(diff_level) not in list(map(str, chapter_qs.keys())):
                chapter_qs[str(diff_level)] = []
        for level in chapter_qs.keys():
            level_qs = chapter_qs[level]
            while len(level_qs) < 5:
                tag = TagGenerator()
                while Question.objects.filter(q_unique_id=tag).exists():
                    tag = TagGenerator()
                q_number = len(level_qs) + 1
                question = Question.objects.create(
                        user=user,
                        q_subject=subject,
                        q_moduel=module,
                        q_chapter=chapter,
                        q_difficulty=level,
                        q_unique_id=tag,
                        q_number=q_number
                    )
                level_qs.append(question.q_unique_id)
    #
    return module_content

def filter_drag_drop_selection(global_objects, selected_options, item_name):
    # remove disabled moduels from selection_option
    order = {}
    for idd, item in enumerate(selected_options.copy()):
        position = int(item.split('_')[0])
        if position < 0:
            selected_options.remove(item)
        else:
            order[position] = item
    filtered_2 = ['_'.join(item.split('_')[1:]) for item in selected_options]
    # remove ordered and active moduels from the global list
    spec_objs = []
    global_objects_final = []
    for idd, a in enumerate(global_objects):
        if a[item_name] in filtered_2:
            spec_objs.append(global_objects[idd])
        else:
            global_objects_final.append(global_objects[idd])
    # extract order from dict 2
    od = collections.OrderedDict(sorted(order.items()))
    selected_options_final = []
    for key, value in od.items():
        value = '_'.join(value.split('_')[1:])
        for item in spec_objs:
            if item[item_name] == value:
                selected_options_final.append(item)
    return global_objects_final, selected_options_final


def insert_new_spec_order(ordered_items, content, item_name):
    for idd, item in enumerate(ordered_items):
        if item not in content:
            content[item] = {}
            if item_name != 'point':
                content[item]['content'] = {}
            if item_name == 'chapter':
                content[item]['questions'] = {}
        content[item]['position'] = idd
        content[item]['active'] = True
    for item in content:
        if item not in ordered_items:
            content[item]['position'] = -1
            content[item]['active'] = False
    return content


def extract_active_spec_content(spec_content):
    points = []
    questions = []
    for module in spec_content.keys():
        module_content = spec_content[module]['content']
        if spec_content[module]['active'] is True:
            for chapter in module_content.keys():
                chapter_questions = spec_content[module]['content'][chapter]['questions']
                if spec_content[module]['content'][chapter]['active'] is True:
                    list_chapter_questions = [arr for arr in chapter_questions.values()]
                    flattened_list = list(chain(*list_chapter_questions))
                    questions += flattened_list
                    chapter_content = spec_content[module]['content'][chapter]['content']
                    for topic in chapter_content.keys():
                        if chapter_content[topic]['active'] is True:
                            for point in chapter_content[topic]['content'].keys():
                                if chapter_content[topic]['content'][point]['active'] is True:
                                    points.append(point)
    return points, questions


def extract_active_spec_questions(spec_content):
    questions = []
    for module in spec_content.keys():
        module_content = spec_content[module]['content']
        if spec_content[module]['active'] is True:
            for chapter in module_content.keys():
                chapter_questions = spec_content[module]['content'][chapter]['questions']
                if spec_content[module]['content'][chapter]['active'] is True:
                    list_chapter_questions = [arr for arr in chapter_questions.values()]
                    flattened_list = list(chain(*list_chapter_questions))
                    questions += flattened_list
    return questions


def detect_empty_content(spec_content):
    empty_invalid_content = defaultdict(dict)
    for module in spec_content.keys():
        module_content = spec_content[module]['content']
        if spec_content[module]['active'] is True:
            #
            module_condition = True
            for item in spec_content[module]['content']:
                if spec_content[module]['content'][item]['active'] is True:
                    module_condition = False
            if module_condition:
                empty_invalid_content[module] = {}
                continue
            #
            for chapter in module_content.keys():
                if spec_content[module]['content'][chapter]['active'] is True:
                    #
                    chapter_condition = True
                    for item in spec_content[module]['content'][chapter]['content']:
                        if spec_content[module]['content'][chapter]['content'][item]['active'] is True:
                            chapter_condition = False
                    if chapter_condition:
                        if module not in empty_invalid_content:
                            empty_invalid_content[module] = {}
                        empty_invalid_content[module][chapter] = {}
                        continue
                    #
                    chapter_content = spec_content[module]['content'][chapter]['content']
                    for topic in chapter_content.keys():
                        if chapter_content[topic]['active'] is True:
                            #
                            topic_condition = True
                            for item in spec_content[module]['content'][chapter]['content'][topic]['content']:
                                if spec_content[module]['content'][chapter]['content'][topic]['content'][item]['active'] is True:
                                    topic_condition = False
                            if topic_condition:
                                if module not in empty_invalid_content:
                                    empty_invalid_content[module] = {}
                                if chapter not in empty_invalid_content[module]:
                                    empty_invalid_content[module][chapter] = {}
                                empty_invalid_content[module][chapter][topic] = True
    return empty_invalid_content


def order_full_spec_content(content):
    def sort_spec_dict_by_position(dictionary):
        ordered_content = collections.OrderedDict(
                sorted(
                    dictionary.items(),
                    key=lambda item: item[1]['position']
                )
            )
        return ordered_content
    ordered_moduels = sort_spec_dict_by_position(content)
    for key_1, value_1 in ordered_moduels.items():
        chapter_content = value_1['content']
        ordered_chapters = sort_spec_dict_by_position(chapter_content)
        for key_2, value_2 in ordered_chapters.items():
            topic_content = value_2['content']
            ordered_topics = sort_spec_dict_by_position(topic_content)
            for key_3, value_3 in ordered_topics.items():
                point_content = value_3['content']
                ordered_points = sort_spec_dict_by_position(point_content)
                ordered_topics[key_3]['content'] = ordered_points
            ordered_chapters[key_2]['content'] = ordered_topics
        ordered_moduels[key_1]['content'] = ordered_chapters
    return ordered_moduels


def order_live_spec_content(content):
    def sort_spec_dict_by_position(dictionary):
        items = [item for item in dictionary.items() if item[1]['active'] == True]
        ordered_content = collections.OrderedDict(
                sorted(
                    items,
                    key=lambda item: item[1]['position']
                )
            )
        return ordered_content
    ordered_moduels = sort_spec_dict_by_position(content)
    for key_1, value_1 in ordered_moduels.items():
        chapter_content = value_1['content']
        ordered_chapters = sort_spec_dict_by_position(chapter_content)
        for key_2, value_2 in ordered_chapters.items():
            topic_content = value_2['content']
            ordered_topics = sort_spec_dict_by_position(topic_content)
            for key_3, value_3 in ordered_topics.items():
                point_content = value_3['content']
                ordered_points = sort_spec_dict_by_position(point_content)
                ordered_topics[key_3]['content'] = ordered_points
            ordered_chapters[key_2]['content'] = ordered_topics
        ordered_moduels[key_1]['content'] = ordered_chapters
    return ordered_moduels


def TranslatePointContent(content):
    out_desc = ''
    if str(type(content)) == "<class 'dict'>":
        for idd, value in content.items():
            for idd2, value2 in value.items():
                if idd2 == 'text':
                    out_desc += value2 + '\n'
                if idd2 == 'img':
                    info = value2['img_info']
                    name = value2['img_name']
                    out_desc += f"!({info})[{name}]" + '\n'
    else:
        out_desc = content
    return out_desc


def TranslateQuestionContent(content):
    out_desc = ''
    if str(type(content)) == "<class 'dict'>":
        for idd, value in content.items():
            for idd2, value2 in value.items():
                if idd2 == 'text':
                    out_desc += value2 + '\n'
                if idd2 == 'img':
                    info = value2['img_info']
                    name = value2['img_name']
                    out_desc += f"!({info})[{name}]" + '\n'
    else:
        out_desc = content
    return out_desc


def TranslateQuestionAnswer(content):
    out_desc = ''
    if str(type(content)) == "<class 'dict'>":
        for idd, value in content.items():
            for idd2, value2 in value.items():
                if idd2 == 'text':
                    out_desc += value2 + '\n'
                if idd2 == 'img':
                    info = value2['img_info']
                    name = value2['img_name']
                    out_desc += f"!({info})[{name}]" + '\n'
    else:
        out_desc = content
    return out_desc


def is_valid_youtube_embed(link):
    # Regular expression pattern for embedded YouTube links
    embed_pattern = r'^https?://(?:www\.)?youtube\.com/embed/[-\w]+$'
    # Check if the link matches the embedded pattern
    if re.match(embed_pattern, link):
        return True
    return False



def monthly_sum_data_list(
            Model,
            labels,
            time_field='date_joined',
            n_months=n_months,
            count_fn=Count('id')
        ):
    data = [0 for _ in range(n_months)]
    data_aggr = Model.objects.annotate(
            month=TruncMonth(time_field)
        ).values(
            'month'
        ).annotate(
            count=count_fn
            ).values('month', 'count')[0:n_months]
    for count in data_aggr:
        month = count['month'].strftime('%b %y')
        user_count = count['count']
        if month in labels:
            idd = labels.index(month)
            data[idd] = user_count
    return data

def usage_monthly_sum_data_list(
            models, labels, time_field='created_at', n_months=n_months
        ):
    Prompt = [0 for _ in range(n_months)]
    Completion = [0 for _ in range(n_months)]
    Total = [0 for _ in range(n_months)]
    for model in models:
        for field in ['prompt', 'completion', 'total']:
            data_set = monthly_sum_data_list(model, labels, time_field, n_months, Sum(field))
            if field == 'prompt':
                Prompt = [sum(x) for x in zip(Prompt, data_set)]
            if field == 'completion':
                Completion = [sum(x) for x in zip(Completion, data_set)]
            if field == 'total':
                Total = [sum(x) for x in zip(Total, data_set)]
    datasets = []
    for field in [
            ('prompt', Prompt, '#f6c23e'),
            ('completion', Completion, '#1cc88a'),
            ('total', Total, '#36b9cc')
        ]:
        datasets.append({
            "label": field[0].upper(),
            "lineTension": 0.2,
            "backgroundColor": "",
            "borderColor": field[2],
            "pointRadius": 3,
            "pointBackgroundColor": field[2],
            "pointBorderColor": field[2],
            "pointHoverRadius": 3,
            "pointHoverBackgroundColor": "rgba(78, 115, 223, 1)",
            "pointHoverBorderColor": "rgba(78, 115, 223, 1)",
            "pointHitRadius": 10,
            "pointBorderWidth": 2,
            "data":  field[1]
        })
    return datasets

def user_course_monthly_sum_data_list(
            Model,
            labels,
            lessons,
            time_field='date_joined',
            n_months=n_months,
            count_fn=Count('id')
        ):
    data = [0 for _ in range(n_months)]
    data_aggr = Model.objects.filter(lesson__in=lessons).annotate(
            month=TruncMonth(time_field)
        ).values(
            'month'
        ).annotate(
            count=count_fn
            ).values('month', 'count')[0:n_months]
    for count in data_aggr:
        month = count['month'].strftime('%b %y')
        user_count = count['count']
        if month in labels:
            idd = labels.index(month)
            data[idd] = user_count
    return data

def user_course_usage_monthly_sum_data_list(
            models, labels, lessons, time_field='created_at', n_months=n_months
        ):
    Prompt = [0 for _ in range(n_months)]
    Completion = [0 for _ in range(n_months)]
    Total = [0 for _ in range(n_months)]
    for model in models:
        for field in ['prompt', 'completion', 'total']:
            data_set = user_course_monthly_sum_data_list(model, labels, lessons, time_field, n_months, Sum(field))
            if field == 'prompt':
                Prompt = [sum(x) for x in zip(Prompt, data_set)]
            if field == 'completion':
                Completion = [sum(x) for x in zip(Completion, data_set)]
            if field == 'total':
                Total = [sum(x) for x in zip(Total, data_set)]
    datasets = []
    for field in [
            ('prompt', Prompt, '#f6c23e'),
            ('completion', Completion, '#1cc88a'),
            ('total', Total, '#36b9cc')
        ]:
        datasets.append({
            "label": field[0].upper(),
            "lineTension": 0.2,
            "backgroundColor": "",
            "borderColor": field[2],
            "pointRadius": 3,
            "pointBackgroundColor": field[2],
            "pointBorderColor": field[2],
            "pointHoverRadius": 3,
            "pointHoverBackgroundColor": "rgba(78, 115, 223, 1)",
            "pointHoverBorderColor": "rgba(78, 115, 223, 1)",
            "pointHitRadius": 10,
            "pointBorderWidth": 2,
            "data":  field[1]
        })
    return datasets


def performance_index_monthly_sum_data_list(
            Model,
            labels,
            user,
            course,
            time_field='date_joined',
            n_months=n_months,
            count_fn=Count('id')
        ):
    data = [0 for _ in range(n_months)]
    data_aggr = Model.objects.filter(user=user, course=course, track_attempt_number__gt=0).annotate(
            month=TruncMonth(time_field)
        ).values(
            'month'
        ).annotate(
            count=count_fn
            ).values('month', 'count')[0:n_months]
    for count in data_aggr:
        month = count['month'].strftime('%b %y')
        user_count = count['count']
        if month in labels:
            idd = labels.index(month)
            data[idd] = user_count
    return data


def increment_course_subscription_significant_click(user, course, significant_click_name):
    current_month = datetime.now().strftime('%Y%m')
    course_subscription = CourseSubscription.objects.get(user=user, course=course)
    # check and add current month dictionary
    if current_month not in course_subscription.monthly_significant_clicks.keys():
        course_subscription.monthly_significant_clicks[current_month] = {}
    if current_month not in user.monthly_significant_clicks.keys():
        user.monthly_significant_clicks[current_month] = 0
    # check and add significant click field
    if significant_click_name not in course_subscription.monthly_significant_clicks[current_month].keys():
        course_subscription.monthly_significant_clicks[current_month][significant_click_name] = 0
    # increment click
    user.monthly_significant_clicks[current_month] += 1
    course_subscription.monthly_significant_clicks[current_month][significant_click_name] += 1
    course_subscription.save()
    user.save()


def author_user_clicks_data_list(user, month_keys, subscriptions, courses):
    aggrigate_monthly_sum = OrderedDict({key:0 for key in month_keys})
    aggrigate_user_monthly_engagement = OrderedDict({key:defaultdict(float) for key in month_keys})
    course_aggrigate_monthly_clicks = []
    month_active_subscriptions = 0
    creator_percentage_split = settings.CREATOR_PERCENTAGE_SPLIT
    affiliate_percentage_split = settings.AFFILIATE_PERCENTAGE_SPLIT
    #
    course_labels = []
    total_courses_clicks = []
    total_estimated_earning = 0
    # Get all affiliate earnings
    affiliate_promotion_code_id = user.affiliate_promotion_code
    if affiliate_promotion_code_id:
        affiliate_discounted_subscriptions = Discount.objects.filter(promotion_code=affiliate_promotion_code_id, subscription__status__in=['active'], livemode=settings.STRIPE_LIVE_MODE)
        for _discounted_subscription in affiliate_discounted_subscriptions:
            discounted_subscription = _discounted_subscription.subscription
            if 'coupon' in discounted_subscription.discount:
                discount_amount = float(discounted_subscription.plan.amount) * float(discounted_subscription.discount['coupon']['percent_off']/100)
            else:
                discount_amount = 0
            #
            student_plan = discounted_subscription.plan
            total_amount = round(
                    (float(discounted_subscription.plan.amount) - discount_amount)/student_plan.interval_count,
                    2
                )
            total_estimated_earning += (affiliate_percentage_split*float(total_amount))
    # Get all course click earnings
    for course in courses:
        course_subscriptions = subscriptions.filter(course=course)
        total_course_clicks = 0
        for sub in course_subscriptions:
            # Get the total course clicks
            for key in month_keys:
                if key in sub.monthly_significant_clicks.keys():
                    aggrigate_monthly_sum[key] += sum(sub.monthly_significant_clicks[key].values())
                    aggrigate_user_monthly_engagement[key][sub.user.id] += sum(sub.monthly_significant_clicks[key].values())/sub.user.monthly_significant_clicks[key]
            if month_keys[-1] in sub.monthly_significant_clicks.keys():
                month_active_subscriptions += 1
                # Calculate earings for this course clicks
                total_user_clicks = sub.user.monthly_significant_clicks[month_keys[-1]]
                last_month_user_course_clicks = sum(sub.monthly_significant_clicks[month_keys[-1]].values())
                course_clicks_fraction = last_month_user_course_clicks/total_user_clicks
                #
                student_current_subscriptions = Subscription.objects.filter(customer__id=sub.user.id, status__in=['active'], livemode=settings.STRIPE_LIVE_MODE)
                if len(student_current_subscriptions) > 0:
                    student_current_subscription = student_current_subscriptions[0]
                    if student_current_subscription.discount is not None:
                        if 'coupon' in student_current_subscription.discount:
                            discount_amount = float(student_current_subscription.plan.amount) * float(student_current_subscription.discount['coupon']['percent_off']/100)
                        else:
                            discount_amount = 0
                    else:
                        discount_amount = 0
                    #
                    student_plan = student_current_subscription.plan
                    total_amount = round(
                            (float(student_current_subscription.plan.amount) - discount_amount)/student_plan.interval_count,
                            2
                        )
                    total_estimated_earning += (creator_percentage_split*float(total_amount))*course_clicks_fraction
            # get the total clicks for each course
            by_month_clicks = [sum(list(value.values())) for value in sub.monthly_significant_clicks.values()]
            total_course_clicks += sum(by_month_clicks)
        course_labels.append(course.course_name)
        total_courses_clicks.append(total_course_clicks)
    course_aggrigate_monthly_clicks = (course_labels, total_courses_clicks)
    return aggrigate_monthly_sum, course_aggrigate_monthly_clicks, month_active_subscriptions, total_estimated_earning, aggrigate_user_monthly_engagement


def confirm_question_checks(question):
    message = ''
    status = True
    if len(str(question.q_content)) < 15:
        message = f'Failed to pass the minimum question length requirement of at least 15 characters.'
        status = False
        return message, status
    if len(str(question.q_answer)) < 15:
        message = f'Failed to pass the minimum question length requirement of at least 15 characters.'
        status = False
        return message, status
    return message, status 


def confirm_point_checks(point):
    message = ''
    status = True
    if len(str(point.p_content)) < 100:
        message = f'Failed to pass the minimum question length requirement of at least 100 characters.'
        status = False
        return message, status
    return message, status 









