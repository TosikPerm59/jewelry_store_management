
class Testing:

    @staticmethod
    def show_session_data(request, show_products=False, show_invoice=False):
        print()
        print('SessionData: Keys')
        for key, value in request.session._session_cache.items():
            print('key =', key, ',', 'len =', len(request.session._session_cache[key]))
        print()
        if show_products is True:
            print('SessionData: Products:')
            for key, value in request.session._session_cache['product_objects_dict_for_view'].items():
                print(key, value)
            print()
        if show_invoice is True:
            print('SessionData: InvoiceData:')
            if 'invoice' in request.session._session_cache.keys():
                for key, value in request.session._session_cache['invoice'].items():
                    print(key, value)
                print()

    @staticmethod
    def show_context_data(context, show_lists=False):
        print('Context Data:')
        for key, value in context.items():
            if show_lists is True:
                if isinstance(value, list):
                    print('Ключ =', key)
                    for item in value:
                        print(item)
                else:
                    if isinstance(value, list):
                        print(key, 'len=', len(value))
                    else:
                        print(key, '=', value)
            else:
                if isinstance(value, list):
                    print(key, 'len=', len(value))
                else:
                    print(key, '=', value)
        print()


