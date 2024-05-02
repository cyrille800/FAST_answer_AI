Apres avoir cloner le projet, vous devez :
- installer les librairies avec pip install -r requirements.txt
- creer un fichier .env avec les informations ci=apres
    *  GEMINI_API_KEY = "..."
    *  ANTHROPIC_API_KEY = "..."
    *  OPEN_AI_GPT_KEY = "..."
    *  MATHPIX_API_KEY = "..."
    *  MATHPIX_app_id = "..."

    *  MODEL_OPEN_AI_GPT = "gpt-4-turbo"
    *  MODEL_OPUS_AI_GPT = "claude-3-opus-20240229"
    *  MODEL_GEMINI_AI = "gemini-1.5-pro-latest"
 
      Note: remplacer les ... par les cles AI des differentes solutions, vous n'etes pas oblige de tout renseigner, mais vous devez obligatoirement renseigner un cle pour (GEMINI_API_KEY, ou soit ANTHROPIC_API_KEY, ou soit OPEN_AI_GPT_KEY )
            et vous devez egalement renseigner une cle pour MATHPIX_app_id, rendez vous sur les different plateformer pour creer un compte en tant que developpeur et vous creer une cles api.
