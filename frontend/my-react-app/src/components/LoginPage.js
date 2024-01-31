import React from 'react';
import { useForm } from 'react-hook-form';

const LoginPage = () => {
  const { register, handleSubmit } = useForm();

  const onSubmit = (data) => {
    console.log(data);
    // Perform login request to your backend with passwordless token
    // On successful login, redirect to the main interface
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input
        type="email"
        placeholder="Email"
        {...register('email', { required: true })}
      />
      <input
        type="tel"
        placeholder="Phone Number"
        {...register('number', { required: true })}
      />
      <input
        type="text"
        placeholder="Name"
        {...register('name', { required: true })}
      />
      <button type="submit">Login</button>
    </form>
  );
};

export default LoginPage;