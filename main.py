# main.py

import os, sys
import callsignHead

# 查找首次数字出现的索引（除了首位）
# 因为呼号前缀的首位可能是数字，如果返回索引为0表示没找到
def get_first_number_index(call_sign:str):
    find_index:int = 0
    for i in range(1, len(call_sign)):
        if f'{call_sign[i]}' in "0123456789":
            find_index = i
            break
    return find_index

# 分割呼号的各个部分，方便进行分析。
def split_call_sign(call_sign:str):
    call_sign_part = dict()
    # 分割有前缀或者后缀的呼号
    slash_split_list = call_sign.split(sep='/')
    if len(slash_split_list) == 1:
        pass
    elif len(slash_split_list) == 2:
        if len(slash_split_list[0]) < len(slash_split_list[1]):
            call_sign_part['prefix'] = slash_split_list[0]
            call_sign = slash_split_list[1]
        elif len(slash_split_list[0]) > len(slash_split_list[1]):
            call_sign_part['suffix'] = slash_split_list[1]
            call_sign = slash_split_list[0]
        else:
            raise Exception('无法分辨呼号主体与前后缀，因为他们长度一样。')
    elif len(slash_split_list) == 3:
        call_sign_part['prefix'] = slash_split_list[0]
        call_sign = slash_split_list[1]
        call_sign_part['suffix'] = slash_split_list[2]
    else:
        raise Exception('无法剥离呼号主体与前后缀，因为“/”的个数太多。')

    # 分割呼号主体
    len_of_callsign = len(call_sign)
    if call_sign[0] in "BFGIKMNRW" and call_sign[1].isdigit():
        call_sign_part['head'] = call_sign[0]
        call_sign_part['mid'] = call_sign[1]
        call_sign_part['tail'] = call_sign[2:]
    elif len_of_callsign == 4:
        call_sign_part['head'] = call_sign[:2]
        call_sign_part['mid'] = call_sign[2]
        call_sign_part['tail'] = call_sign[3:]
    elif 5 <= len_of_callsign <= 7:
        if call_sign[2].isdigit():
            call_sign_part['head'] = call_sign[:2]
            call_sign_part['mid'] = call_sign[2]
            call_sign_part['tail'] = call_sign[3:]
        else:
            call_sign_part['head'] = call_sign[:3]
            call_sign_part['mid'] = call_sign[3]
            call_sign_part['tail'] = call_sign[4:]
    else:
        raise Exception(f"呼号的长度不正确{len_of_callsign}。")

    return call_sign_part

china_part_code = {
    '0':set(('新疆', '西藏')),
    '1':set(('北京', '业余卫星业务')),
    '2':set(('黑龙江', '辽宁', '吉林')),
    '3':set(('天津', '河北', '内蒙古', '山西')),
    '4':set(('上海', '山东', '江苏')),
    '5':set(('浙江', '江西', '福建')),
    '6':set(('安徽', '河南', '湖北')),
    '7':set(('湖南', '广东', '广西', '海南')),
    '8':set(('四川', '重庆', '贵州', '云南')),
    '9':set(('陕西', '甘肃', '宁夏', '青海'))
}

def get_head_mean(head_str:str):
    head_mean = dict()
    head_mean['country'] = callsignHead.get_callsign_head_assign(callsign_head=head_str)
    if head_mean['country'] == {'中华人民共和国'}:
        radio_type = "呼号第二位不在规定分配范围的业余电台"
        if head_str[1] in 'GHIDA':
            radio_type = 'A类、B类、C类业余电台'
        elif head_str[1] == 'J':
            if callsign_part['mid'] == '1':
                radio_type = '卫星业余电台'
            else:
                radio_type = '业余信标台'
        elif head_str[1] == 'R':
            radio_type = '业余中继台'
        elif head_str[1] in 'BCEFKSTYZ':
            radio_type = '其它业余电台(由国无管机构分配)'
        head_mean['type'] = radio_type
    return head_mean

if __name__ == '__main__':
    if len(sys.argv) == 2:
        head_str:str = sys.argv[1]
    else:
        head_str:str = input("Call sign: ")

    # 解析呼号的各个组成部分
    callsign_part = split_call_sign(head_str)
    #print(callsign_part)

    # 解析呼号头部
    if 'head' in callsign_part.keys():
        head_mean = get_head_mean(callsign_part['head'])
        print(f"指配给：{head_mean['country']}")
        if 'type' in head_mean.keys():
            print(f"电台类型：{head_mean['type']}")

            # 解析中国业余呼号的中部和尾部
            if '其它' not in head_mean['type'] and '不在' not in head_mean['type']:
                area_set = china_part_code[callsign_part['mid']]
                print(f"国内{callsign_part['mid']}区电台：{area_set}")

                prov_set = callsignHead.get_china_prov_by_callsign_tail(callsign_part['tail'])
                intersection = area_set & prov_set
                print(f'国内分配省份：{intersection}')
                print(f"省内编码：{callsignHead.get_callsign_part_sum(callsign_part['tail'])}")

    # 解析呼号前缀
    if 'prefix' in callsign_part.keys():
        prefix:str = callsign_part['prefix']
        if prefix.startswith('B'):
            head_mean = f"国内{prefix[-1]}区：{china_part_code[prefix[-1]]}"
        else:
            head_mean = get_head_mean(prefix)['country']
        print(f"异地发射：{head_mean}")

    # 解析呼号后缀
    if 'suffix' in callsign_part.keys():
        suffix = callsign_part['suffix']
        if suffix == 'M':
            suffix_mean = '在陆地上移动'
        elif suffix == 'AM':
            suffix_mean = '在空中移动'
        elif suffix == 'MM':
            suffix_mean = '在海上移动'
        elif suffix == 'QRP':
            suffix_mean = '小功率电台'
        elif suffix == 'P':
            suffix_mean = '便携电台'
        print(f'后缀{suffix}    {suffix_mean}')