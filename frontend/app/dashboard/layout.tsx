'use client';

import { Fragment, useState } from 'react';
import { Dialog, Menu, Transition } from '@headlessui/react';
import {
  Bars3Icon,
  HomeIcon,
  UsersIcon,
  ChatBubbleLeftRightIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline';
import { logout } from '@/utils/auth';
import clsx from 'clsx';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
  { name: 'Students', href: '/dashboard/students', icon: UsersIcon },
  { name: 'Chat', href: '/dashboard/chat', icon: ChatBubbleLeftRightIcon },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <>
      <div>
        <Transition.Root show={sidebarOpen} as={Fragment}>
          <Dialog
            as="div"
            className="fixed inset-0 flex z-40 md:hidden"
            onClose={setSidebarOpen}
          >
            <Transition.Child
              as={Fragment}
              enter="transition-opacity ease-linear duration-300"
              enterFrom="opacity-0"
              enterTo="opacity-100"
              leave="transition-opacity ease-linear duration-300"
              leaveFrom="opacity-100"
              leaveTo="opacity-0"
            >
              <Dialog.Overlay className="fixed inset-0 bg-gray-600 bg-opacity-75" />
            </Transition.Child>
            <Transition.Child
              as={Fragment}
              enter="transition ease-in-out duration-300 transform"
              enterFrom="-translate-x-full"
              enterTo="translate-x-0"
              leave="transition ease-in-out duration-300 transform"
              leaveFrom="translate-x-0"
              leaveTo="-translate-x-full"
            >
              <div className="relative flex-1 flex flex-col max-w-xs w-full bg-white">
                <div className="absolute top-0 right-0 -mr-12 pt-2">
                  <button
                    type="button"
                    className="ml-1 flex items-center justify-center h-10 w-10 rounded-full focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
                    onClick={() => setSidebarOpen(false)}
                  >
                    <span className="sr-only">Close sidebar</span>
                    <XMarkIcon
                      className="h-6 w-6 text-white"
                      aria-hidden="true"
                    />
                  </button>
                </div>
                <div className="flex-1 h-0 pt-5 pb-4 overflow-y-auto">
                  <div className="flex-shrink-0 flex items-center px-4">
                    <h1 className="text-xl font-bold">Campus AI Admin</h1>
                  </div>
                  <nav className="mt-5 px-2 space-y-1">
                    {navigation.map((item) => (
                      <a
                        key={item.name}
                        href={item.href}
                        className="group flex items-center px-2 py-2 text-base font-medium rounded-md text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                      >
                        <item.icon
                          className="mr-4 h-6 w-6 text-gray-400 group-hover:text-gray-500"
                          aria-hidden="true"
                        />
                        {item.name}
                      </a>
                    ))}
                  </nav>
                </div>
                <div className="flex-shrink-0 flex border-t border-gray-200 p-4">
                  <button
                    className="flex-shrink-0 group block"
                    onClick={() => logout()}
                  >
                    <div className="flex items-center">
                      <div>
                        <div className="text-base font-medium text-gray-700">
                          Log out
                        </div>
                      </div>
                    </div>
                  </button>
                </div>
              </div>
            </Transition.Child>
            <div className="flex-shrink-0 w-14">
              {/* Force sidebar to shrink to fit close icon */}
            </div>
          </Dialog>
        </Transition.Root>

        {/* Static sidebar for desktop */}
        <div className="hidden md:flex md:w-64 md:flex-col md:fixed md:inset-y-0">
          <div className="flex-1 flex flex-col min-h-0 border-r border-gray-200 bg-white">
            <div className="flex-1 flex flex-col pt-5 pb-4 overflow-y-auto">
              <div className="flex items-center flex-shrink-0 px-4">
                <h1 className="text-xl font-bold">Campus AI Admin</h1>
              </div>
              <nav className="mt-5 flex-1 px-2 bg-white space-y-1">
                {navigation.map((item) => (
                  <a
                    key={item.name}
                    href={item.href}
                    className={clsx(
                      'group flex items-center px-2 py-2 text-sm font-medium rounded-md',
                      'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    )}
                  >
                    <item.icon
                      className="mr-3 h-6 w-6 text-gray-400 group-hover:text-gray-500"
                      aria-hidden="true"
                    />
                    {item.name}
                  </a>
                ))}
              </nav>
            </div>
            <div className="flex-shrink-0 flex border-t border-gray-200 p-4">
              <button
                className="flex-shrink-0 w-full group block"
                onClick={() => logout()}
              >
                <div className="flex items-center">
                  <div>
                    <div className="text-sm font-medium text-gray-700">
                      Log out
                    </div>
                  </div>
                </div>
              </button>
            </div>
          </div>
        </div>

        {/* Content area */}
        <div className="md:pl-64 flex flex-col flex-1">
          <div className="sticky top-0 z-10 md:hidden pl-1 pt-1 sm:pl-3 sm:pt-3 bg-gray-100">
            <button
              type="button"
              className="-ml-0.5 -mt-0.5 h-12 w-12 inline-flex items-center justify-center rounded-md text-gray-500 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-500"
              onClick={() => setSidebarOpen(true)}
            >
              <span className="sr-only">Open sidebar</span>
              <Bars3Icon className="h-6 w-6" aria-hidden="true" />
            </button>
          </div>
          <main className="flex-1">
            <div className="py-6">
              <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8">
                {children}
              </div>
            </div>
          </main>
        </div>
      </div>
    </>
  );
}