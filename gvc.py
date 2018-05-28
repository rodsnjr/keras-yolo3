import pandas as pd
import os
import get_image_size
import pickle

def parse_csv_annotations(annotations, img_dir, cache_name, labels):
    """
        Parsear o CSV com um pandas dataframe
    """
    all_annots = []
    label_counts = {}
    repeated_annots = {}
    df = pd.read_csv(annotations)

    labels.insert(0, "background")

    def get_image_size_(image_path):
        try:
            width, height = get_image_size.get_image_size(image_path)
            return width, height
        except Exception:
            width, height = -1, -1

    def get_image_info(item):
        return {
                'filename': os.path.join(img_dir, item.frame),
                'object': [get_object_info(item)],
                'height': w,
                'width': h
        }

    def get_object_info(item):
        return {
            'name': labels[item.class_id],
            'xmax': item.xmax,
            'xmin': item.xmin,
            'ymax': item.ymax,
            'ymin': item.ymin
        }

    index = 0
    for k, item in df.iterrows():
        label_counts[labels[item.class_id]] = label_counts.get(labels[item.class_id], -1) + 1

        w, h = get_image_size_(os.path.join(img_dir, item.frame))
        
        if item.frame in repeated_annots:
            index = repeated_annots[item.frame]
            if len(all_annots) > index:
                all_annots[repeated_annots[item.frame]]['object'].append(get_object_info(item))
            else:
                print(index, all_annots, len(all_annots))
                break
        else:
            repeated_annots[item.frame] = index
            all_annots.append(get_image_info(item))
            index += 1
    
    if "background" in label_counts:
        del label_counts['background']
    if "background" in labels:
        del labels[0]

    cache = {'all_insts': all_annots, 'seen_labels': label_counts}
    with open(cache_name, 'wb') as handle:
        pickle.dump(cache, handle, protocol=pickle.HIGHEST_PROTOCOL)

    return all_annots, label_counts