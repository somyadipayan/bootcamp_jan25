export default{
    data() {
        return {
            user: null,
            role: null,
            authorized: false
        }
    },
    async created() {
        await this.checkAuthorization();
    },
    methods: {
        async checkAuthorization() {
            const access_token = localStorage.getItem('access_token');
            if(!access_token) {
                this.user = null;
                this.authorized = false;
                return;
            }
            this.user = await this.getUserInfo(access_token);
                   
        },
        async getUserInfo(access_token) {
            const response = await fetch('http://localhost:5000/getuserinfo', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${access_token}`
                }
            })
            const data = await response.json();
            if(response.ok) {
                this.role = data.role; 
                this.authorized = true; 
                return data;
            }
            else {
                this.role = null;
                this.authorized = false;
                return null;
            }
            
        },
        logout() {
            fetch('http://localhost:5000/logout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
            }).then(() => {
                localStorage.removeItem('access_token');
                this.user = null;
                this.role = null;
                this.authorized = false;
                this.$router.push('/login');
            }).catch(err => console.log(err));
        }
    }
}
