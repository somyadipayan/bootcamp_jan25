<template>
    <NavBar />
    <div class="container mt-5">
        <div class="card">
            <div class="card-header">
                <h1>Login Here</h1>
            </div>
            <div class="card-body">
                <form @submit.prevent="login">

                    <div class="form-group">
                        <label for="name">Username</label>
                        <input type="text" v-model="username" class="form-control" id="name"
                            placeholder="Username">
                    </div>
        
                    <div class="form-group">
                        <label for="password">Password</label>
                        <input type="password" v-model="password" class="form-control" id="password"
                            placeholder="Enter your password">
                    </div>
                    
                    <button type="submit" class="btn btn-primary mt-3">Login</button>
                </form>
            </div>
        </div>
    </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue';
export default {
    components: { NavBar },
    data() {
        return {
            "username": '',
            "password": ''
        }
    },
    methods: {
        async login() {
            const response = await fetch('http://localhost:5000/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    "username": this.username,
                    "password": this.password
                })
            })
            const data = await response.json()
            if(response.ok) {
                alert(data.message)
                localStorage.setItem('access_token', data.access_token) 
                this.$router.push('/')
            }
            else{
                alert(data.error)
            }
        }
    }
}
</script>