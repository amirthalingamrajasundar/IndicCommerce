from langchain.prompts import PromptTemplate

# Define a prompt with variables
prompt = PromptTemplate(
    input_variables=["query", "products"],
    template="""
        {query}

        Context:
        {products}
    """
)