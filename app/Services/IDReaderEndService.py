class IDReaderEndService:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(IDReaderEndService, cls).__new__(cls, *args, **kwargs)
        return cls._instance

id_reader_end_service = IDReaderEndService()
id_reader_end_service2 = IDReaderEndService()



