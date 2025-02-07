<template>
    <NavBar />
    <h1 class="page-title">{{ adRequest.name }}</h1>
    <div class="message-container">
        <div class="payment-card">
            <p class="payment-amount">Payment amount: ${{ adRequest.paymentAmount }}</p>
            <button class="btn btn-success" @click="acceptAdRequest(adRequest.id)">Accept with Last Offer</button>
        </div>

        <div class="messages-list" ref="messagesList">
            <div v-for="message in messages" :key="message.time" class="message-bubble" :class="{
                'current-user': message.sent_by === this.role,
                'other-user': message.sent_by !== this.role
            }">
                <div class="message-content">
                    {{ message.message }}
                    <div v-if="message.temporary_payment_amount" class="payment-update">
                        Updated offer: ${{ message.temporary_payment_amount }}
                    </div>
                </div>
                <div class="message-time">
                    {{ message.time }}
                </div>
            </div>
        </div>

        <div class="input-container">
            <input type="text" v-model="message" placeholder="Type your message..." class="message-input"
                @keyup.enter="sendMessage">
            <input type="number" v-model="updated_temporary_payment_amount" placeholder="Amount" class="payment-input">
            <button class="send-button" @click="sendMessage">
                Send
            </button>
        </div>
    </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue';
import userMixin from '@/mixins/userMixin';

export default {
    name: 'NegotiationPage',
    components: { NavBar },
    mixins: [userMixin],
    data() {
        return {
            adRequest: {},
            messages: [],
            message: '',
            updated_temporary_payment_amount: 0
        }
    },
    mounted() {
        const adRequest_id = this.$route.params.id;
        this.fetchData(adRequest_id);
    },
    methods: {
        async acceptAdRequest(adRequest_id) {
            try {
                const response = await fetch(`http://localhost:5000/adrequest/finalize`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
                    },
                    body: JSON.stringify({ ad_request_id: adRequest_id })
                });
                const data = await response.json();
                console.log(data);
                if (response.ok) {
                    alert(data.message)
                    if (this.role === 'influencer'){
                        this.$router.push('/influencer-dashboard')
                    }
                    else{
                        this.$router.push('/my-campaigns')
                    }
                } else {
                    alert(data.error)
                    
                }
            } catch (error) {
                this.message = 'Failed to accept request: ' + error.message;
                this.messageClass = 'alert-danger';
            }
        },

        async fetchData(adRequest_id) {
            try {
                const response = await fetch(`http://localhost:5000/negotiation/${adRequest_id}`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
                    }
                });
                const data = await response.json();
                if (response.ok) {
                    this.adRequest = data.adRequest;
                    this.messages = data.messages;
                    this.updated_temporary_payment_amount = data.adRequest.temporary_payment_amount;
                    this.$nextTick(() => {
                        this.scrollToBottom();
                    });
                }
            } catch (error) {
                console.error(error);
            }
        },
        async sendMessage() {
            try {
                const response = await fetch('http://localhost:5000/negotiation', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
                    },
                    body: JSON.stringify({
                        ad_request_id: this.adRequest.id,
                        message: this.message,
                        temporary_payment_amount: this.updated_temporary_payment_amount
                    })
                });
                if (response.ok) {
                    this.fetchData(this.adRequest.id);
                    this.message = '';
                    this.updated_temporary_payment_amount = 0;
                }
            } catch (error) {
                console.error(error);
            }
        },
        scrollToBottom() {
            const container = this.$refs.messagesList;
            if (container) {
                container.scrollTop = container.scrollHeight;
            }
        }
    }
}
</script>
<style scoped>
.page-title {
    text-align: center;
    margin: 20px 0;
    color: #2c3e50;
}

.message-container {
    max-width: 800px;
    height: 80vh;
    margin: 20px auto;
    padding: 20px;
    display: flex;
    flex-direction: column;
}

.payment-card {
    background: #f8f9fa;
    border-radius: 12px;
    padding: 15px 20px;
    margin-bottom: 20px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.payment-amount {
    margin: 0;
    font-weight: 500;
    color: #2c3e50;
}

.messages-list {
    flex: 1;
    overflow-y: auto;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 12px;
    margin-bottom: 20px;
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.05);
}

.message-bubble {
    max-width: 70%;
    margin: 10px 0;
    padding: 12px 16px;
    border-radius: 18px;
    word-break: break-word;
    animation: fadeIn 0.3s ease-in;
}

.current-user {
    background: #007bff;
    color: white;
    margin-left: auto;
    border-bottom-right-radius: 4px;
}

.other-user {
    background: #e9ecef;
    color: #2c3e50;
    margin-right: auto;
    border-bottom-left-radius: 4px;
}

.message-content {
    font-size: 1em;
    line-height: 1.4;
}

.message-time {
    font-size: 0.75em;
    opacity: 0.8;
    margin-top: 6px;
    text-align: right;
}

.current-user .message-time {
    color: rgba(255, 255, 255, 0.8);
}

.other-user .message-time {
    color: rgba(0, 0, 0, 0.6);
}

.input-container {
    display: flex;
    gap: 10px;
    padding: 10px;
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.message-input {
    flex: 1;
    padding: 12px 16px;
    border: 1px solid #e9ecef;
    border-radius: 8px;
    outline: none;
    transition: border-color 0.3s ease;
}

.message-input:focus {
    border-color: #007bff;
}

.payment-input {
    width: 100px;
    padding: 12px;
    border: 1px solid #e9ecef;
    border-radius: 8px;
    outline: none;
}

.send-button {
    padding: 12px 24px;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: background 0.3s ease;
}

.send-button:hover {
    background: #0056b3;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.payment-update {
    font-size: 0.8em;
    margin-top: 8px;
    padding: 4px 8px;
    background-color: rgba(255, 255, 255, 0.1);
    border-radius: 6px;
    display: inline-block;
}

.current-user .payment-update {
    background-color: rgba(0, 0, 0, 0.15);
}

.other-user .payment-update {
    background-color: rgba(0, 0, 0, 0.05);
}
</style>