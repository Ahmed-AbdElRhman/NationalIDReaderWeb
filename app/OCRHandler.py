import logging
logger = logging.getLogger(__name__)
class OCRHandler:
    def iDReader(self, filepath):
        
        logger.info("Hiiiiiiiiiiiiiiiiiiiiiiiiiiiii iDReader here")
        for i in range(100000):
            print(f"iDReader iteration {i + 1} of 10")
            logger.info(f"iDReader iteration {i + 1} of 10")
            logger.debug(f"Starting calculation for value: {i}")
        """
        Simulates reading ID data from a file and returns sample data.
        
        Args:
            filepath (str): Path to the file to be processed (not used in this sample)
            
        Returns:
            dict: Sample ID data with expected fields
        """
        # This is sample data - in a real implementation, this would come from OCR processing
        sample_data = {
            'firstname': 'John',
            'parname': 'Doe',
            'nationalID': '12345678901234',
            'address': '123 Main St, Cairo',
            'birthdate': '01/01/1990',
            'gov': 'Cairo',
            'gender': 'Male'
        }
        
        return sample_data