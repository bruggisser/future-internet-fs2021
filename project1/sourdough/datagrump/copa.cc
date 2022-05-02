#include <iostream>

#include "copa.hh"
#include "timestamp.hh"

using namespace std;

Copa::Copa( const bool debug )
  : debug_( debug ), Q( std::queue<int>() ), standing_rtt( std::multiset<int>() )
{}

/* Get current window size, in datagrams */
unsigned int Copa::get_window_size()
{
    return window_size;
}

void Copa::inc(){
    window_size += v / (delta * window_size);
}

void Copa::dec(){
    window_size -= v / (delta * window_size);
    window_size = max(window_size, 1.0);
}

void Copa::ack_received( const uint64_t send_timestamp_acked, const uint64_t timestamp_ack_received ){
    // update v every 3 RTT
    if(v_ack_sent < timestamp_ack_received){
        v_ack_sent = timestamp_ack_received + minRTT;
        if((v_window > window_size && v_up) || (v_window < window_size && !v_up)){
            v_ack_count_rtt++;
        } else {
            v_ack_count_rtt = 0;
            v = 1.0;
        }
        v_up = v_window > window_size;
        v_window = window_size;
        if(v_ack_count_rtt == 3){
            v = v * 2.0;
            v_ack_count_rtt = 0;
            if(debug_) cerr << "v = " << v << endl;
        }
    }

    int R = timestamp_ack_received - send_timestamp_acked;
    if(R < minRTT) minRTT = R;
    Q.push(R);
    standing_rtt.insert(R);
    // take minimum of last approx. 1 RTT
    while(standing_rtt.size() > window_size){
        int first = Q.front();
        auto it = standing_rtt.find(first);
        standing_rtt.erase(it);
        Q.pop();
    }
    double standing = (double) *standing_rtt.begin();
    double d_q = max(standing - minRTT, 1.0); // avoid div0
    double lambda = 1.0 / (delta * d_q);

    if(window_size / standing <= lambda){
        inc();
    } else {
        dec();
    }
}