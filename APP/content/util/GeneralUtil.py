import io
import random
import string
import collections
import markdown
import ruamel.yaml



def TagGenerator():
    x = ''.join(
            random.choices(string.ascii_letters + string.digits, k=10)
        ).lower()
    return x


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
    tab = '	'
    output = ''
    output += 'hidden_details:' + '\n'
    output += tab + 'point_title: ' + str(content['details']['hidden']['0']['point_title']) + '\n'
    point_content = content['details']['hidden']['0']['content']
    for pos, item in point_content.items():
        pos = int(pos)
        if item['vid']:
            video = item['vid']
            output += tab + f'vid_{pos+1}:' + '\n'
            output += tab + tab + 'video_title: ' + video['vid_title'] + '\n'
            output += tab + tab + 'video_link: ' + video['vid_link'] + '\n'
    #
    out = '```yaml' + '\n' + output + '```'
    out_desc = ''
    desc = content['details']['description']
    for idd, value in desc.items():
        for idd2, value2 in value.items():
            if idd2 == 'text':
                out_desc += value2 + '\n'
            if idd2 == 'img':
                info = value2['img_info']
                name = value2['img_name']
                out_desc += f"!({info})[{name}]" + '\n'
    return out + out_desc


def TranslateQuestionContent(content):
    output = ''
    output += '+++ Meta_details:' + '\n'
    output += 'question_type: ' + str(content['details']['head']['0']['q_type']) + '\n'
    output += 'question_difficulty: ' + str(content['details']['head']['0']['q_difficulty']) + '\n'
    output += '\n\n+++ Question:\n'
    for n in range(len(content['details']['questions'])):
        part = content['details']['questions'][str(n)]
        part_name = part['q_part']
        part_mark = part['q_part_mark']
        part_content = part['content']
        output += f'\nPartName_{part_name}'
        output += f'_PartMark_{part_mark}:\n'
        for n2 in range(len(part_content)):
            item = part_content[str(n2)]
            if 'text' in item:
                string = item['text'].replace('\n', '')
                output += f'{string}\n'
            if 'img' in item:
                img_name = item['img']['img_name']
                img_info = item['img']['img_info']
                output += f'!({img_info})'
                output += f'[{img_name}]\n'
    output += '\n\n+++ Answer:' + '\n'
    for n in range(len(content['details']['answers'])):
        part = content['details']['answers'][str(n)]
        part_name = part['q_part']
        part_content = part['content']
        output +=f'\nAnswerPart_PartName_{part_name}\n'
        for n2 in range(len(part_content)):
            item = part_content[str(n2)]
            if 'text' in item:
                string = item['text'].replace('\n', '')
                output += f'{string}\n'
            if 'img' in item:
                img_name = item['img']['img_name']
                img_info = item['img']['img_info']
                output += f'!({img_info})'
                output += f'[{img_name}]\n'
    return output





