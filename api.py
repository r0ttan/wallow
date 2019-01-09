import responder
import redis, json, time, os

baseurl = "api/v0.2"
api = responder.API(debug=True)

def configurewall(confile):
    with open(confile) as cf:
        conf = json.load(cf)
    ehost = os.environ.get('REDIS_URL')
    esec = os.environ.get('REDIS_APITOK')
    eport = os.environ.get('REDIS_PORT')
    #print(conf)
    return redis.Redis(host=ehost, port=eport, password=esec, decode_responses=True)
    #return redis.Redis(host=conf['redis']['host'], port=conf['redis']['port'], password=conf['redis']['sec'], decode_responses=True)

r = configurewall("wall.conf")

@api.route('/')
async def default(req, resp):
    resp.text = f"thisis : not_json_response"

@api.route('/test/{arg}')
def test(req, resp, *, arg):
    print("Test url_for")
    resp.media = api.url_for(checksaldo, account="abc123")


@api.route('/deposit/{account}/{amount}')
def deposit(req, resp, *, account, amount):
    p = r.pipeline()
    p.lpushx("account:{}:transactions".format(account), "T{}+{}".format(r.time()[0],amount))
    p.hincrby("account:{}:balance".format(account), "balance", amount)
    p.execute()
    #resp.media = { "url": url_for('checksaldo', accountname=account, _external=True) }
    resp.media = { "url": url_for('checksaldo', accountname=account, _external=True) }

@api.route('/withdraw/{account}/{amount}')
def withdraw(req, resp, *, account, amount):
    print("WITHDRAW")
    am = int(amount)
    if am > 0:
        print("positive amount, inverting")
        am *= -1
        print(am)
    p = r.pipeline()
    p.lpushx("account:{}:transactions".format(account), "T{}{}".format(r.time()[0],am))
    p.hincrby("account:{}:balance".format(account), "balance", am)
    p.execute()
    print("EXECUTED")
    resp.media = {"url": url_for('checksaldo', accountname=account, _external=True)}

@api.route('/checksaldo/{account}')
def checksaldo(req, resp, *, account):
    resp.media = result = r.hgetall("account:{}:balance".format(account))

@api.route('/transactions/{account}/{listlen}')
def checktrans(req, resp, *, account, listlen):
    result = r.lrange("account:{}:transactions".format(account), 0, listlen)
    print(result)
    for res in result:
        eptime = res[1:11]
        tran = res[11:]
        if eptime != "":
            print(time.strftime('%Y%m%d %H%M', time.gmtime(int(eptime))), tran)
        else:
            print("eptime: {}, tran:{}".format(eptime, tran))
    resp.media = result


if __name__ == '__main__':
    api.run()
