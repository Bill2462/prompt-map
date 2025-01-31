from dataclasses import dataclass

@dataclass
class ProcessingError(Exception):
    msg: str
    last_model_output: str
    model_input: str = None
    
    def get_str(self):
        err_msg = f"Error: '{self.msg}' "
        if self.model_input:
            err_msg += f"Model input: '{self.model_input}'"
        
        err_msg += f"Last model output: '{self.last_model_output}'"
        return err_msg
