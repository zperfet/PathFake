# 主要用于数据的预处理；对已有数据进行一定的整合和转换

from config import *
from data_io import *
from treelib import Tree
from preprocess4wae import *
from get_args import _args
import re


# 根据树文件夹生成路径id文件和路径文本文件
# 输入:树文件夹,每棵树对应一个文件,文件中每一行都是一对父子节点,以及节点的时间
# 输出:
# 1)根据树文件生成的路径id,每一行对应一条路径中全部节点的id,从根节点到叶子节点
# 2)根据树文件生成的路径text,每一行对应一条路径中的全部文本,文本顺序和id对应
def generate_path_ids_and_texts(tree_dir_path, path_ids_save_path, path_texts_save_path):
    names = os.listdir(tree_dir_path)
    id2text_dict = get_text_dict()
    path_sum = 0
    all_path_ids = []
    all_path_texts = []
    for cnt, name in enumerate(names):
        path = join(tree_dir_path, name)
        source_id = name.split('.')[0]
        with open(path, 'r')as f:
            lines = [line.strip() for line in f.readlines()]
        tree = Tree()
        tree.create_node(identifier=source_id)
        if lines[0] != '':
            for line in lines:
                line = line.split('\t')
                p_node, c_node = line[0], line[2]
                try:
                    tree.create_node(identifier=c_node, parent=p_node)
                except Exception:
                    pass
        # 根据树生成路径
        path_ids = tree.paths_to_leaves()
        all_path_ids += ['\t'.join(line) for line in path_ids]
        # 获取每一条路径对应源文本的标签
        # path_label = [id2label_dict[line[0]] for line in path_ids]
        path_texts = [[id2text_dict[i] for i in line] for line in path_ids]
        path_texts = ['\t'.join(line) for line in path_texts]
        all_path_texts += path_texts
        # for i in range(len(path_ids)):
        #     all_path_texts.append(path_texts[i] + '\t' + path_label[i])
        path_sum += len(path_ids)
    with open(path_ids_save_path, 'w')as f:
        f.write('\n'.join(all_path_ids) + '\n')
    with open(path_texts_save_path, 'w')as f:
        f.write('\n'.join(all_path_texts) + '\n')


# 根据树文件夹生成路径id文件和路径文本文件
# 输入:树文件夹,每棵树对应一个文件,文件中每一行都是一对父子节点,以及节点的时间
# 输出:
# 1)根据树文件生成的路径id,每一行对应一条路径中全部节点的id,从根节点到叶子节点
# 2)根据树文件生成的路径text,每一行对应一条路径中的全部文本,文本顺序和id对应
def generate_path_ids_and_texts_early(tree_dir_path, max_time, save_path):
    names = os.listdir(tree_dir_path)
    tree_ids_dict = dict()
    path_cnt = 0
    node_cnt = 0
    for cnt, name in enumerate(names):
        path = join(tree_dir_path, name)
        source_id = name.split('.')[0]
        tree_ids_dict[source_id] = []
        with open(path, 'r')as f:
            lines = [line.strip() for line in f.readlines()]
        # 将超过max-time的行删除
        lines = [line.split('\t') for line in lines]
        lines = [line for line in lines if len(line) == 4 and
                 float(line[1]) <= max_time and float(line[3]) <= max_time]
        lines = ['\t'.join(line) for line in lines]
        if len(lines) == 0: continue
        tree = Tree()
        tree.create_node(identifier=source_id)
        if lines[0] != '':
            for line in lines:
                line = line.split('\t')
                p_node, c_node = line[0], line[2]
                try:
                    tree.create_node(identifier=c_node, parent=p_node)
                except Exception:
                    pass
        # 根据树生成路径
        path_ids = tree.paths_to_leaves()
        # 获取每一条路径对应源文本的标签
        # path_texts = [[id2text_dict[i] for i in line] for line in path_ids]
        # path_texts = ['\t'.join(line) for line in path_texts]
        # tree_ids_dict[source_id] += path_texts
        tree_ids_dict[source_id] = path_ids
        path_cnt += len(path_ids)
        node_cnt += len(tree.nodes.keys())
    print("max_time:", max_time, "path_nums:", path_cnt, "node_nums:", node_cnt)
    # print("save dict to", save_path)
    save_json_dict(tree_ids_dict, save_path)


# 消除路径文本中的源文本；基于回复文本构建路径
# 输入:
# 1）路径id文件路径，每一行代表一条路径，路径的第一个id是源文本id
# 2）id、文本对应的文本路径
# 输出：路径id对应的文本，其中源文本id消除了源文本
def get_response_path(path_ids_path, save_path):
    # 读取path-ids，并删除源文本的id
    with open(path_ids_path, 'r')as f:
        response_path_ids = [line.strip().split('\t')[1:] for line in f.readlines()]

    # 获取dict(id:text)
    id2text_dict = get_text_dict()

    response_path_texts = []
    for id_lst in response_path_ids:
        tmp_path_text = []
        for id in id_lst:
            tmp_path_text.append(id2text_dict[id])
        response_path_texts.append('\t'.join(tmp_path_text))
    with open(save_path, 'w')as f:
        f.write('\n'.join(response_path_texts) + '\n')


# 根据给定的推特id返回 分词后根据词汇表映射得到的id列表
# token2id_dict_path:词汇表对应路径,根据词汇表返回对应id，如果不存在返回0
# tweet_id:推特文本对应的id,此处为twitter15|16数据集对应的全部ids;注意不同数据集对应的词汇表不同
# save_path:保存tweet_id：tweet_token_ids字典
def tweet_id2_token_ids(vocab_path, tweet_id_lst, save_path):
    # 读取词汇并生成字典
    with open(vocab_path, 'r')as f:
        tokens = [token.strip() for token in f.readlines()]
    token2id_dict = dict()
    for cnt, token in enumerate(tokens):
        token2id_dict[token] = cnt
    tokens_set = set(token2id_dict.keys())
    # 加载id->text字典
    id2text_dict = get_text_dict()
    # 分词
    nlp = spacy.load('en_core_web_sm')
    tokenizer = Tokenizer(nlp.vocab)
    res_dict = dict()
    PATTERN = re.compile(r'\b[^\d\W]{2,20}\b')
    for cnt, tid in enumerate(tweet_id_lst):
        if (cnt + 1) % 1000 == 0:
            print("处理", cnt + 1)
        # 根据id获取文本
        texts = id2text_dict[tid]
        # 文本预处理
        texts = texts.lower()
        # texts = PATTERN.sub(" ", texts)
        texts = ''.join(c if c.isalpha() else ' ' for c in texts)
        texts = emoji_replace(texts)
        texts = delete_special_freq(texts)
        line_tokens = list(map(str, tokenizer(texts)))
        line_ids = [token2id_dict[word] for word in line_tokens if word in tokens_set]
        line_ids = sorted(set(line_ids))
        res_dict[tid] = line_ids
    # 将词典保存到本地
    print('将词典保存到本地')
    save_json_dict(res_dict, save_path)


# 使用特定字符替代特殊字符
# 1）表情：
# 😂1281;😳417;👀68;🙏73;❤85;👏98;🙌101;😭521;
# 😒77;😩173;😷101;👍84;😍158;🎉66;😫50;😔103;
# 💔88;👎56;😊49;😁44;🙅48
def emoji_replace(text):
    emoji_replace_dict = {"😂": " emoji_a ", "😳": " emoji_b ", "👀": " emoji_c ",
                          "🙏": " emoji_d ", "❤": " emoji_e ", "👏": " emoji_f ",
                          "🙌": " emoji_g ", "😭": " emoji_h ", "😒": " emoji_i ",
                          "😩": " emoji_j ", "😷": " emoji_k ", "👍": " emoji_l ",
                          "😍": " emoji_m ", "🎉": " emoji_n ", "😫": " emoji_o ",
                          "😔": " emoji_p ", "💔": " emoji_q ", "😊": " emoji_r ",
                          "😁": " emoji_s ", "🙅": " emoji_t "}
    for k in emoji_replace_dict.keys():
        if k in text:
            text = text.replace(k, emoji_replace_dict[k])
    return text


# 删除句子中类似@和url
def delete_special_freq(text):
    if len(text) < 20: return text
    # print('转换前：', text)
    raw = text
    text = [word for word in text.split() if word[0] != '@']
    text = ' '.join(text)
    # 如果只有@，则保留@
    if text == '': text = raw
    text = text.replace('URL', '')
    # 如果只有url，则保留url
    if text == '': text = raw
    # print('转换后：', text)
    # print()
    return text


# early detection预处理
# 参数：
# 1）树文件夹,每棵树对应一个文件,文件中每一行都是一对父子节点,以及节点的时间
# 2）保存预处理文件的文件夹路径
# 3）最迟的时间段
def early_detection_truncation():
    time_interval = [0, 6, 12, 18, 24, 30, 36, 42, 48, 54, 60, 120]
    # time_interval = [100000000]
    tree15_dir_path = join(data_dir_path, 'TreeTwitter15')
    tree16_dir_path = join(data_dir_path, 'TreeTwitter16')
    for max_time in time_interval:
        save15_path = join(early_detection_dir_path,
                           "early_twitter15_interval%d.json" % max_time)
        save16_path = join(early_detection_dir_path,
                           "early_twitter16_interval%d.json" % max_time)
        generate_path_ids_and_texts_early(tree15_dir_path, max_time, save15_path)
        generate_path_ids_and_texts_early(tree16_dir_path, max_time, save16_path)


if __name__ == '__main__':
    early_detection_truncation()

    path15_vocab4random_path = join(data_dir_path, 'pathTwitter15vocab4random')
    response15_vocab4wae_path = join(data_dir_path, 'response_pathTwitter15vocab4wae')
    path16_vocab4random_path = join(data_dir_path, 'pathTwitter16vocab4random')
    response16_vocab4wae_path = join(data_dir_path, 'response_pathTwitter15vocab4wae')

    random15_vocab_path = join(path15_vocab4random_path, 'vocabulary', 'vocab.txt')
    random16_vocab_path = join(path16_vocab4random_path, 'vocabulary', 'vocab.txt')
    response15_vocab_path = join(response15_vocab4wae_path, 'vocabulary', 'vocab.txt')
    response16_vocab_path = join(response16_vocab4wae_path, 'vocabulary', 'vocab.txt')

    t15_source_lst = get_tweet_id_lst(join(data_dir_path, 'source_tweets15.txt'))
    t16_source_lst = get_tweet_id_lst(join(data_dir_path, 'source_tweets16.txt'))
    t15_response_lst = get_tweet_id_lst(join(data_dir_path, 'tweet_response15_clean.txt'))
    t16_response_lst = get_tweet_id_lst(join(data_dir_path, 'tweet_response16_clean.txt'))

    tweet_id2_token_ids(random15_vocab_path, t15_source_lst + t15_response_lst,
                        join(data_dir_path, "early_random15_ids.json"))
    tweet_id2_token_ids(random16_vocab_path, t16_source_lst + t16_response_lst,
                        join(data_dir_path, "early_random16_ids.json"))
    tweet_id2_token_ids(response15_vocab_path, t15_source_lst + t15_response_lst,
                        join(data_dir_path, "early_response15_ids.json"))
    tweet_id2_token_ids(response16_vocab_path, t16_source_lst + t16_response_lst,
                        join(data_dir_path, "early_response16_ids.json"))
    # 根据树文件生成路径ids和路径texts
    # print('根据树文件生成路径ids和路径texts...')
    # generate_path_ids_and_texts(tree_dir_path, path_ids_path, path_texts_path)
    #
    # # 根据路径ids生成回复路径texts
    # print('根据路径ids生成回复ids...')
    # get_response_path(path_ids_path, path_response_text_raw_path)
    # # 预处理回复路径texts：替换表情包，删除url和@等符号
    #
    # print('预处理回复路径文本...')
    # with open(path_response_text_raw_path, 'r')as f:
    #     lines = [line.strip() for line in f.readlines()]
    # lines = [emoji_replace(line) for line in lines]
    # lines = [delete_special_freq(line) for line in lines]
    # with open(path_response_text_path, 'w')as f:
    #     f.write('\n'.join(lines) + '\n')

    # 为WAE预处理路径文本和回复路径文本
    # print('预处理path文本...')
    # pre4wae(path_vocab4random, path_texts_path, _args.random_vocab_dim - 1)
    # print('预处理response path文本...')
    # pre4wae(response_path_vocab4wae, path_response_text_path, _args.response_vocab_dim - 1)

    # 合并twitter15,16的数据集用于无监督训练
    # pre4wae_response(response_pathTwitter15vocab4wae, path_response15_text_path,
    #                  path_response16_text_path, _args.response_vocab_dim - 1)
