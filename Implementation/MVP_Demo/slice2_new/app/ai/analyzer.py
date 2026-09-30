from typing import Any
import hashlib,json
from .prompts import PROMPT_VERSION,SYSTEM_PROMPT,build_company_prompt
from .provider import BaseAIProvider,AIProviderError
from .schemas import MasterResearchReport
class AIAnalyzer:
    def __init__(self,provider:BaseAIProvider): self.provider=provider
    @staticmethod
    def input_hash(*,evidence:dict[str,Any],review_context:dict[str,Any],previous_key_takeaways:list[str],prompt_version:str=PROMPT_VERSION)->str:
        value=json.dumps({'prompt_version':prompt_version,'evidence':evidence,'review_context':review_context,'previous_key_takeaways':previous_key_takeaways},sort_keys=True,ensure_ascii=False,default=str).encode();return hashlib.sha256(value).hexdigest()
    def analyze_company(self,*,evidence,review_context,previous_key_takeaways,thread_context=None,report_language='en'):
        prompt=build_company_prompt(evidence=evidence,review_context=review_context,previous_key_takeaways=previous_key_takeaways,thread_context=thread_context,report_language=report_language)
        result=self.provider.analyze(system_prompt=SYSTEM_PROMPT,user_prompt=prompt,response_schema=MasterResearchReport)
        return MasterResearchReport.model_validate(result).model_dump(mode='json')
    def analyze_event(self,*,evidence): raise AIProviderError('event_analysis_not_enabled','Use Step 8 targeted research updates.')
