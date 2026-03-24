import anvil.server

def solve_click(self, **event_args):
    problem = self.text_box_1.text

    result = anvil.server.call('solve_text_api', problem)

    if result["status"] == "success":
        self.output_box.text = result["explanation"]
        self.confidence_label.text = f"Confidence: {result['confidence']:.2f}"
    else:
        self.output_box.text = result["message"]