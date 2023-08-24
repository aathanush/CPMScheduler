from enum import verify
from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import numpy as np
import pandas as pd
import networkx as nx
import pandas as pd
import pylab
import matplotlib.pyplot as plt

table={"Activity":[],"Predecessors":[],"Duration":[]}
table["Activity"].append("St")
table["Predecessors"].append(None)
table["Duration"].append(0)


i=0 
b=False
def task_assigner():
    check_condition()
    
    N=entry1.get().strip()
    if not N.isdigit() or int(N)<=0:
        messagebox.showwarning(title="Invalid input", message="The input you have entered is not a natural number. Please try again")
        return
    
    else:
        
        N=int(N)
        top=Toplevel()
        top.geometry("700x200")
        top.title(f"Enter task details for Task {i+1}")
        name_label=Label(top,text="Task name")
        name_label.grid(row=0,column=0)
        name_entry=Entry(top)
        name_entry.grid(row=0,column=1)
        pred_label=Label(top,text="Predecessor(s) name")
        pred_label.grid(row=1,column=0)
        pred_entry=Entry(top)
        pred_entry.grid(row=1,column=1)
        dur_label=Label(top,text="Duration")
        dur_label.grid(row=2,column=0)
        dur_entry=Entry(top)
        dur_entry.grid(row=2,column=1)

        def update_table():
            global i
            name=name_entry.get().strip()
            pred=pred_entry.get().strip()
            dur=dur_entry.get().strip()
            if name==pred:
                messagebox.showerror(title="Invalid input",message="Task name is the same as the predecessor!")
                i-=1
                
            else:
                OK=messagebox.askokcancel("Task verification",message=f"Verify the information you have entered\nTask:{name}\nPredecessors:{pred}\nDuration:{dur}")
                print(OK)
                if not OK:
                    i-=1
                else:
                    global table
                    table["Activity"].append(name)
                    table["Duration"].append(int(dur))
                    table["Predecessors"].append(pred)
                    name_entry.delete(0 ,'end')
                    dur_entry.delete(0 ,'end')
                    pred_entry.delete(0 ,'end')
                    i+=1
                print(i)
                if i<N:
                    top.title(f"Enter task details for Task {i+1}")
                elif i==N:
                    top.title(f"Enter the details of the end node")
                    name_entry.insert(0,"End")
                    dur_entry.insert(0,'0')
                else:
                    global b
                    b=True
                    top.destroy() 
                    print("Top destroyed")  
                    after_function()
                         
        
        button=Button(top,text="Enter details",command=update_table)
        button.grid(row=3,column=0)
        # top.mainloop()


def after_function():
    def find_all_paths(graph, start, end, path=[]):
        path = path + [start]
        if start == end:
            return [path]
        if not start in graph.keys():
            return []
        paths = []
        for node in graph[start]:
            if node not in path:
                newpaths = find_all_paths(graph, node, end, path)
                for newpath in newpaths:
                    paths.append(newpath)
        return paths




    def topologicalSortUtil(graph_edges,v,visited,stack):
        visited[v] = True
        for i in graph_edges[v]:
            if visited[i] == False:
                topologicalSortUtil(graph_edges,i,visited,stack)
        stack.insert(0,v)

    def topologicalSort(graph_edges,visited,stack):
        for i in graph_edges.keys():
            if visited[i] == False:
                topologicalSortUtil(graph_edges,i,visited,stack)

    df=pd.DataFrame(table)
    df.to_csv("table.csv")
    Df = pd.read_csv("table.csv")
    graph_edges={x:[] for x in Df["Activity"]}
    weights ={k:int(v) for k,v in zip(Df["Activity"],Df["Duration"])} 
    for index, row in Df.iterrows():
        if str(row["Predecessors"])=='nan':
            pass
        else:
            acts=str(row["Predecessors"]).split(" ")
            for act in acts:
                graph_edges[act].append(row['Activity'])

    paths = find_all_paths(graph_edges, 'St', 'End')
    time_t=[sum([weights[z] for z in path]) for path in paths]
    index_p = time_t.index(max(time_t))

    node_data = {k:{"ES":0,"EF":0,"LS":0,"LF":0} for k in graph_edges.keys()} 
    pred={k:str(v).split(" ") for k,v in zip(Df["Activity"],Df["Predecessors"])}
    stack=[]
    visited={k:False for  k in graph_edges.keys()}

    topologicalSort(graph_edges,visited,stack)

    stack.pop(0)

    while(stack!=[]):
        top = stack[0]
        max_f = np.NINF
        for i in pred[top]:
            if(max_f < node_data[i]["EF"]):
                max_f = node_data[i]["EF"]

        node_data[top]["ES"] = max_f
        node_data[top]["EF"] = max_f + weights[top]
        stack.pop(0)


    visited={k:False for  k in graph_edges.keys()}
    topologicalSort(graph_edges,visited,stack)
    r_stack=stack[::-1]
    node_data[r_stack[0]]["LS"]=node_data[r_stack[0]]["ES"]
    node_data[r_stack[0]]["LF"]=node_data[r_stack[0]]["EF"]
    r_stack.pop(0)

    while(r_stack!=[]):
        top = r_stack[0]
        min_s = np.Inf
        for i in graph_edges[top]:
            if(min_s > node_data[i]["LS"]):
                min_s = node_data[i]["LS"]

        node_data[top]["LF"] = min_s
        node_data[top]["LS"] = min_s - weights[top]
        r_stack.pop(0)

    text="\nNode\tES\tEF\tLS\tLF\n"
    for  k,v in node_data.items():
        text+=f'{k}\t{v["ES"]}\t{v["EF"]}\t{v["LS"]}\t{v["LF"]}\n'
    messagebox.showinfo(title="Critical Path",message=f"Critical path is:{[i for i in stack if node_data[i]['LF']-node_data[i]['EF']==0]}"+text)
    window.destroy()
    G = nx.DiGraph(directed=True)
    G.add_nodes_from(graph_edges.keys())
    for key in graph_edges.keys():
        G.add_edges_from([(key,v) for v in graph_edges[key]], weight=weights[key])

    red_edges = list(zip(paths[index_p],paths[index_p][1:]))

    node_col = ['yellow' if node not in paths[index_p] else 'red' for node in G.nodes()]
    edge_col = ['black' if edge not in red_edges else 'red' for edge in G.edges()]
    edge_labels=dict([((u,v,),d['weight']) for u,v,d in G.edges(data=True)])

    pos=nx.random_layout(G)
    nx.draw_networkx(G,pos,node_color= node_col,node_size=600)
    nx.draw_networkx_edges(G,pos,edge_color= edge_col)
    nx.draw_networkx_edge_labels(G,pos,edge_labels=edge_labels)
    plt.title("Critical Path Duration: "+str(time_t[index_p])+" weeks")
    plt.show()


def check_condition():
    print("Inside check condition")
    if b:
        print("B is true, executing after function")
        top.withdraw()
        after_function()
        window.after(1000, check_condition) 
window = Tk()
window.title("CPM scheduler")
window.minsize(width=400,height=400)
window.config(padx=50,pady=50)

#Image
canvas = Canvas(width=200,height=200)
image = PhotoImage(file="logo.png")
canvas.create_image(100,100,image=image)
canvas.grid(row=0,column=1)

#Number of tasks
label1 = Label(text="Number of tasks ", font=("courier",10,"bold"))
label1.grid(row=1,column=0)
entry1 = Entry( window, width=52 )
entry1.grid(row=1,column=1)
entry1.focus()
button1 = ttk.Button(text="Enter",command=task_assigner)
button1.grid(row=1, column=2)

# window.after(1000, check_condition)  # Start checking condition after 1000 milliseconds (1 second)
window.mainloop()



