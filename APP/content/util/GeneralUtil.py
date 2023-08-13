import io
import re
import random
import string
import collections
from collections import defaultdict
import markdown
import ruamel.yaml
from content.models import Question

from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth


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
            if str(diff_level) not in chapter_qs.keys():
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


current_month = datetime.now().date()
n_months = 6

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
