from ..buffer import Buffer

# testing creation of buffer
def test_create_buffer():
    buffer = Buffer()
    assert isinstance(buffer, Buffer)
    pass


def test_remember_buffer():
    buffer = Buffer()
    state = "state"
    prob = [1,2,3,4,5,6,7]
    buffer.remember_upper_conf(state, prob)
    assert len(buffer.data) > 0 
    (rem_state, rem_prob) = buffer.data[0]
    assert rem_state == state
    assert rem_prob == prob
    assert rem_prob[0] == 1
    pass

def test_remember_result():
    buffer = Buffer()
    buffer.result = 1
    assert buffer.result == 1
    pass
