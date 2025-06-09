import glob
import pandas as pd
from deepforest.utilities import read_file

def Ryoungseob_2023():
    xmls = glob.glob("/orange/ewhite/DeepForest/Ryoungseob_2023/train_datasets/annotations/*.xml")

    #Load and format xmls
    annotation_list = []   
    for xml_path in xmls:
        try:
            annotation = read_file(xml_path)
        except:
            continue
        annotation_list.append(annotation)
    annotations = pd.concat(annotation_list, ignore_index=True)      
    annotations["label"] = "Animal"
    annotations["source"] = "Kwon et al. 2023"  
    annotations["split"] = "train"
    
    # Add full path to images
    annotations["image_path"] = annotations.image_path.apply(lambda x: "/orange/ewhite/DeepForest/Ryoungseob_2023/train_datasets/images/{}".format(x))
    annotations.to_csv("/orange/ewhite/DeepForest/Ryoungseob_2023/train_datasets/images/train.csv")

if __name__ == "__main__":
    Ryoungseob_2023()