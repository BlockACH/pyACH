import matplotlib.pyplot as plt

result = {'882': 15519, '6D4': 949, '8DA': 0, 'C45': 0, '666': 0, 'E15': 5475, 'C72': 328, 'FB4': 3901, '219': 6005, '4AD': 39923, 'CCC': 6224, '170': 5172, '6AB': 0, '838': 132, '22D': 0, '48C': 450, 'B31': 0, 'FCB': 225, 'E75': 679, '75D': 297, '46E': 8432, 'E0C': 335, 'AB5': 2, 'B89': 0, '18C': 1350, 'EE0': 114, '0B1': 0, '717': 215, 'E07': 0, '1F6': 956, 'B30': 1016, '5BD': 358, 'EDB': 773, 'CE3': 540, 'A0D': 0, 'EA0': 3786, '269': 242, '101': 2621, '552': 292, '481': 0, 'F73': 0, 'B63': 6958, 'BA4': 1813, 'A1D': 825, 'A28': 13530, '49A': 0, '940': 987, '519': 0, 'DD3': 8091, '62F': 612, '7BA': 1990, 'F8E': 441, '822': 6522, '5E0': 4020, '682': 0}

a = result.values()

plt.bar([1,2,3,4,5,6],loan_grade,color='#99CC01',alpha=0.8,align='center',edgecolor='white')

plt.xlabel('Bank')
plt.ylabel('Tx amount')

plt.title('Histogram of Bank tx amount')

plt.legend(['Ach'], loc='upper right')

plt.grid(color='#95a5a6',linestyle='--', linewidth=1,axis='y',alpha=0.4)

plt.xticks(a, result.keys())
plt.show()
