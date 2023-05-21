import io
import random
import string
import collections
from collections import defaultdict
import markdown
import ruamel.yaml
from content.models import Question



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
    for idd, value in content.items():
        for idd2, value2 in value.items():
            if idd2 == 'text':
                out_desc += value2 + '\n'
            if idd2 == 'img':
                info = value2['img_info']
                name = value2['img_name']
                out_desc += f"!({info})[{name}]" + '\n'
    return out_desc


def TranslateQuestionContent(content):
    output = ''
    return content 


def TranslateQuestionAnswer(content):
    output = ''
    return content



