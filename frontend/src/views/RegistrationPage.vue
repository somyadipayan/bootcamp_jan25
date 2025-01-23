<template>
    <NavBar />
    <div class="container mt-5">
        <div class="card">
            <div class="card-header">
                <h1>Register Here</h1>
            </div>
            <div class="card-body">
                <form @submit.prevent="register">
                    <div class="form-group">
                        <label for="role">Role</label>
                        <select v-model="form.role" class="form-control" id="role" for="role" required>
                            <option value="sponsor">Sponsor</option>
                            <option value="influencer">Influencer</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="name">Username</label>
                        <input type="text" v-model="form.username" class="form-control" id="name"
                            placeholder="Username">
                    </div>
                    <div class="form-group">
                        <label for="email">Email</label>
                        <input type="email" v-model="form.email" class="form-control" id="email"
                            placeholder="Enter your email">
                    </div>
                    <div class="form-group">
                        <label for="password">Password</label>
                        <input type="password" v-model="form.password" class="form-control" id="password"
                            placeholder="Enter your password">
                    </div>
                    <div v-if="form.role === 'sponsor'">
                        <div class="form-group">
                            <label for="company_name">Company Name</label>
                            <input type="text" v-model="form.company_name" class="form-control" id="company_name" placeholder="Company Name">
                        </div>
                        <div class="form-group">
                            <label for="industry">Industry</label>
                            <input type="text" v-model="form.industry" class="form-control" id="industry" placeholder="Industry">
                        </div>
                        <div class="form-group">
                            <label for="budget">Budget</label>
                            <input type="number" v-model="form.budget" class="form-control" id="budget" placeholder="Budget">
                        </div>
                    </div>
                    <div v-if="form.role === 'influencer'">
                        <div class="form-group">
                            <label for="name">Name</label>
                            <input type="text" v-model ="form.name" class="form-control" id="name" placeholder="Name">
                        </div>
                        <div class="form-group">
                            <label for="category">Category</label>
                            <input type="text" v-model="form.category" class="form-control" id="category" placeholder="Category">
                        </div>
                        <div class="form-group">
                            <label for="niche">Niche</label>
                            <input type="text" v-model="form.niche" class="form-control" id="niche" placeholder="Niche">
                        </div>
                        <div class="form-group">
                            <label for="reach">Reach</label>
                            <input type="number" v-model="form.reach" class="form-control" id="reach" placeholder="Reach">
                        </div>
                    </div>
                    <button type="submit" class="btn btn-primary mt-3">Register</button>
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
            form: {
                role: '',
                username: '',
                email: '',
                password: '',
                // sponsor specific
                company_name: '',
                industry: '',
                budget: 0,
                // influencer specific
                name: '',
                category: '',
                niche: '',
                reach: 0,
            }
        }
    },
    methods: {
        async register() {
            console.log(this.form)
            const role = this.form.role
            const response = await fetch('http://localhost:5000/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(this.form)
            })
            const data = await response.json()
            if(response.ok) {
                alert(data.message)
                this.$router.push('/about')
            }
            else{
                alert(data.error)
            }
        }
    }
}
</script>

<style scoped></style>