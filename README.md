# Parking Violation Prediction using Graph Colvolution Networks

Controlled parking systems in cities provide designated parking zones and allow citizens easily find parking spaces increasing comfort and potentially reducing traffic and pollution. However, illegally occupied parking spaces can negatively affect the accuracy of these systems, diminishing their benefits. This work presents a semi-supervised deep learning approach for fine-grained parking violation rate prediction using graph neural networks, which can capture both the spatial and temporal dynamics of parking systems and driver behavior, providing a valuable tool for controlled parking systems. The proposed method addresses several challenges faced in this task, including the need to appropriately construct temporal graph-based training datasets and design a model that can handle missing values. Additionally, the method includes a novel semi-supervised data augmentation and smoothing technique to mitigate the effect of small amounts of annotated data and/or missing data in the training dataset. The proposed method was evaluated using a large-scale dataset from Thessaloniki’s on-street public parking system and found to significantly improve the accuracy of parking violation prediction compared to state-of-the-art approaches.

The main contribution of this work is a semi-supervised deep learning approach that employs graph neural networks capable of capturing both the spatial and temporal dynamics of parking systems and driver’s behaviors, im- proving the accuracy of parking violation prediction compared to the existing state-of-the-art approaches.To give you a better understanding of our project, the pipeline of our model is illustrated in the figure below:

<div align="center">
  <img src="https://user-images.githubusercontent.com/44779987/190924742-13ba3d19-7b18-4e37-9ca3-e35d68de6377.png" alt="1" style="max-width: 400px;"/>
</div>

To overcome the aforementioned challenges we propose:

1. An efficient pipeline for constructing temporal graph-based datasets for controlled on-street parking systems.

<div align="center">
  <img src="https://github.com/nikgeokar/parking_stgcn/files/11301989/Figure15_N.pdf" alt="2" width="350"/>
</div>

2. A temporal graph convolutional model design that can cope with miss- ing values that are typically present during inference.

<div align="center">
  <img src="https://github.com/nikgeokar/parking_stgcn/files/11301993/Final6_N.pdf" alt="3" width="350"/>
</div>

3. A novel semi-supervised temporal and spatial data augmentation and smoothing technique that can cope with the small number of annotations and/or missing data present in the training dataset.

<div align="center">
  <img src="https://github.com/nikgeokar/parking_stgcn/files/11301997/Figure5_N.pdf" alt="4" width="350"/>
</div>




Please note that, due to GDPR regulations, the dataset containing historical checks of the municipal police is not publicly available. Therefore, we have included a demo file named "Scan_Data_Reg_2.3.csv" that contains 100 randomly generated records.
