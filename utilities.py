def get_context(query, retriever, config):
    retriever.search_kwargs = config
    relevant_docs= retriever.get_relevant_documents(query = query)

    print("Total Relevant Documents Found: {}".format(len(relevant_docs)))
    # for doc in relevant_docs:
    #     print("====================================")
        # print(doc.page_content)  
    # context =  [doc for doc in relevant_docs]
    context =  "\n\n".join([doc.page_content for doc in relevant_docs])
    return context


def get_context_scraped(query, retriever, config):
    retriever.search_kwargs = config
    relevant_docs= retriever.get_relevant_documents(query = query)

    print("Total Relevant Documents Found: {}".format(len(relevant_docs)))
    for doc in relevant_docs:
        print("====================================")
        print(doc.page_content)  
    context =  [doc for doc in relevant_docs]
    context = "\n\n".join(["{}\nSource URL: {}".format(doc.page_content, doc.metadata.get("url", "URL not available")) for doc in relevant_docs])
    return context


