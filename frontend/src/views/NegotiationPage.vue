<template>
    <NavBar />
    <h1> {{ adRequest.name }} </h1>
    <div class="message-container">
        <div class="card">
            <p> Temporary Payment: ${{ adRequest.temporary_payment_amount }} </p>
        </div>

        <div class="messages" v-for="message in messages" :key="message.time">
            <div class="message"
            :class="{ 'sent-by-sponsor': message.sent_by === 'sponsor' , 'sent-by-influencer': message.sent_by === 'influencer' }">
            <span class="message-content"> {{ message.message }} </span>
            <span class="message-time"> {{ message.time }} </span>
        </div>
    </div>
    <div class="row mt-3">
        <input class="col-7 mr-2" type="text" v-model="message" placeholder="Enter your message">
        <input class="col-3 mr-2" type="text" v-model="updated_temporary_payment_amount" placeholder="$$$">
        <button class="col"@click="sendMessage">Send</button>
    </div>
    </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue';
export default {
    name: 'NegotiationPage',
    components: { NavBar },
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
        async fetchData(adRequest_id) {
            try {
                const response = await fetch(`http://localhost:5000/negotiation/${adRequest_id}`,{
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
                    console.log(data.adRequest);
                    this.updated_temporary_payment_amount = data.adRequest.temporary_payment_amount
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
                const data = await response.json();
                if (response.ok) {
                    console.log("message_recieved")
                    this.fetchData(this.adRequest.id);
                    this.message = '';
                }
            } catch (error) {
                console.error(error);
            }
        }
    }
}
</script>

<style scoped>
.message-container {
    max-width: 800px;
    height: 80vh;
    overflow-y: scroll;
    padding: 20px;
    margin: 20px auto;
    border: 1px solid #ccc;
    border-radius: 5px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.messages {
    display: flex;
    flex-direction: column;
    gap: 5px;
}

.message {
    padding: 10px;
    border-radius: 5px;
    max-width: 70%;
    word-wrap: break-word;
    margin-top: 10px;
}

.message.sent-by-sponsor {
    background-color: #f2f2f2;
    margin-right: auto;
}

.message.sent-by-influencer {
    background-color: #007bff;
    margin-left: auto;
}

.message-content {
    font-size: 1em;
    color: #333;
    margin: 5px;
}


.message-time {
    font-size: 0.75em;
    color: #fffcfc;
    opacity: 0.8;
    margin-top: 5px;
}

</style>