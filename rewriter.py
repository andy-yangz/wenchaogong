import argparse
import numpy as np
import random
import jieba.posseg as pseg
from itertools import product

def is_contain_chinese(check_str):
    """
    判断字符串中是否包含中文
    :param check_str: {str} 需要检测的字符串
    :return: {bool} 包含返回True， 不包含返回False
    """
    for ch in check_str:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False

class LexicalAugmenter:
    def __init__(self, method='w2v'):
        if method=='w2v':
            import synonyms
            self.synonyms = synonyms
        elif method=="bert":
            pass
        elif method=="cilin":
            pass
    
    def select_position(self, words):
        valid_pos = [i for i,word in enumerate(words) if is_contain_chinese(word)]
        random.shuffle(valid_pos)
        return valid_pos
        # return random.sample(valid_pos, k=num)
        
    def augment(self, text, num=1):
        words, tags = zip(*pseg.cut(text))
        select_pos = self.select_position(words)
        new = list(words)
        count = 0
        for i in select_pos:
            sims, scores = self.synonyms.nearby(words[i])
            sims, scores = sims[1:], scores[1:]
            keep = [sims[j] for j in range(len(sims)) if (scores[j]>0.75 and list(pseg.cut(sims[j]))[0].flag==tags[i])]
            if not keep: continue
            choiced = random.choice(keep)
            count += 1
            new[i] = choiced
            if count >= num:
                break
        result = "".join(new)
        if result == text:
            print(f"No replacement for {text}.")
            return []
        return new
    
    def generate_from_cands(self, cands):
        combinations = list(product(*cands))
        results = []
        for combi in combinations:
            result = " ".join(combi)
            results.append(result)
        return results
    
    def get_all_candidates(self, text):
        words, tags = zip(*pseg.cut(text))
        cands = []
        for i, word in enumerate(words):
            if not is_contain_chinese(word): 
                cands.append([word])
                continue
            sims, scores = self.synonyms.nearby(word, 5)
            keep = [sims[j] for j in range(len(sims)) if (scores[j]>0.75 and list(pseg.cut(sims[j]))[0].flag==tags[i])]
            if word not in keep:
                keep.append(word)
            cands.append(keep)
        all_cands = self.generate_from_cands(cands)
        return all_cands

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rewrite Sentences.")
    parser.add_argument('--input', type=str, help="Input path")
    
    augmenter = LexicalAugmenter('w2v')
    text = "这个好好看，为什么不拍电视剧啊"
    
    new = augmenter.augment(text)